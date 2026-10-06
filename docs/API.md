# API.md

Internal modules (no external HTTP API yet). Components:
- DiscoveryService.discover_leads(params)
- WebsiteAnalyzer.analyze(website)
- BusinessClassifier.classify(lead)
- OpportunityDetector.detect(lead)
- LeadScorer.score(lead)
- EmailGenerator.generate(lead)
- EmailSender.send(to, subject, body)
- LeadRepository.create_or_update(lead)
