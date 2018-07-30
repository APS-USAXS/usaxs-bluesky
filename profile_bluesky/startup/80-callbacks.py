print(__file__)

# custom callbacks


# collect last scan's documents into doc_collector.documents
doc_collector = APS_callbacks.DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)


# write scans to SPEC data file
specwriter = APS_filewriters.SpecWriterCallback()
# make the SPEC file in /tmp (assumes OS is Linux)
specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
print("writing to SPEC file: " + specwriter.spec_filename)
