import os
import dns.resolver
import concurrent.futures
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from .models import DNSRecord  # Import your model
from tqdm import tqdm
import time

MAX_RETRIES = 3  # Maximum number of retries for DNS queries
NUM_THREADS = 5  # Number of concurrent threads

def query_domain(domain):
    for retry in range(MAX_RETRIES):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8']  # Use Google's DNS server

            txt_records = resolver.query(domain, 'TXT', lifetime=5.0)
            for txt_record in txt_records:
                # Save data into the database
                DNSRecord.objects.create(domain=domain, txt_record=txt_record.to_text())
            return  # Return on success
        except dns.resolver.NoAnswer:
            DNSRecord.objects.create(domain=domain, txt_record='No TXT record found')
            return  # Return on NoAnswer
        except dns.resolver.NXDOMAIN:
            DNSRecord.objects.create(domain=domain, txt_record='Domain not found')
            return  # Return on NXDOMAIN
        except dns.exception.Timeout:
            if retry < (MAX_RETRIES - 1):
                print(f"Retrying {domain} after a timeout...")
            else:
                DNSRecord.objects.create(domain=domain, txt_record='DNS query timed out')
        except Exception as e:
            DNSRecord.objects.create(domain=domain, txt_record=f'Error: {str(e)}')

def upload_text_file(request):
    if request.method == 'POST':
        text_file = request.FILES.get('text_file')
        print(text_file)

        if text_file:
            # Save the file in the media folder using MEDIA_ROOT
            file_path = os.path.join(settings.MEDIA_ROOT, text_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in text_file.chunks():
                    destination.write(chunk)

            # Read domain names from the uploaded text file
            with open(file_path, 'r') as file:
                domain_list = [line.strip() for line in file]

            # Perform DNS queries for each domain using concurrent threads
            progress_bar = tqdm(total=len(domain_list), desc="Processing Domains", unit="domain")

            def update_progress_bar(*_):
                progress_bar.update(1)

            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                futures = {executor.submit(query_domain, domain): domain for domain in domain_list}

                for future in concurrent.futures.as_completed(futures):
                    domain = futures[future]
                    update_progress_bar()

            progress_bar.close()

            # Redirect after a successful file upload
            return render(request, 'search.html', {})

    return render(request, 'upload.html', {})


def search_domains(request):
    if request.method == 'POST':
        domain_name = request.POST.get('domain_name', '')

        # Query the database for the given domain name
        search_results = DNSRecord.objects.filter(domain__iexact=domain_name)

        return render(request, 'search.html', {'search_results': search_results, 'search_query': domain_name})

    return render(request, 'search.html', {'search_results': None, 'search_query': None})

