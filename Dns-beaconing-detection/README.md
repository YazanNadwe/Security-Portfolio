# DNS Beaconing Detection Lab (Wazuh + BIND + TheHive + Cortex)

A local lab that simulates DNS beaconing traffic (random 12-character subdomains under one parent domain at a fixed ~5-second interval), detects it with a Wazuh correlation rule, creates a TheHive alert and case, and maps the activity to MITRE ATT&CK.

> Educational lab only. All domains are internal (lab.local) and non-routable. No external infrastructure is involved.

## Architecture

| Host | Role |
|------|------|
| Ubuntu 24.04 | BIND9 (internal DNS for lab.local), Wazuh manager/indexer/dashboard, TheHive, Cortex (Docker) |
| Kali Linux | Traffic generator ([dns_sim.py](dns_sim.py)) |
| Windows 10 | Sysmon + Wazuh agent, uses the lab DNS |

Network: isolated host-only VMware network (192.168.239.0/24).

## Detection Logic

| Rule | Level | Purpose |
|------|-------|---------|
| 100199 | 3 | Base rule: A query under lab.local decoded from the BIND query log |
| 100200 | 10 | Frequency rule: 20 matching events within 120 seconds (if_matched_sid 100199) |

MITRE ATT&CK: T1568.002 (Domain Generation Algorithms), T1071.004 (DNS).

## Pipeline

1. BIND logs queries to /var/log/named/query.log.
2. Wazuh logcollector reads the file. A custom decoder tags the events.
3. Rule 100199 matches each lab.local query; rule 100200 fires at 20 matches in 120 s.
4. The custom-thehive integration creates an alert in TheHive automatically.
5. The alert is manually promoted to a case, observables (domain, source IP) are added, and TTPs are mapped.
6. Cortex analyzers are run on the observables. VirusTotal was executed but returned an error (see Limitations).

## Setup Summary

1. Install BIND9, create zone lab.local, and enable query logging in named.conf.local.
2. Verify with named-checkzone and dig.
3. Run [dns_sim.py](dns_sim.py) on Kali (40 queries, 5-second interval).
4. Add a localfile entry for /var/log/named/query.log in ossec.conf.
5. Add the decoder and rules to local_rules.xml. Fix the rule structure so 100200 references 100199, then validate with wazuh-analysisd -t.
6. Configure the custom-thehive integration in ossec.conf.
7. Open the alert in TheHive, promote it to a case, add observables and TTPs.
8. Run Cortex analyzers on the observables.

## Screenshots

| File | Content |
|------|---------|
| 01-bind-zone-ok.png | BIND zone check and DNS resolution |
| 02-dns-query-log.png | BIND query log showing random subdomains |
| 03-wazuh-threat-hunting.png | Wazuh Threat Hunting: rule 100200 alongside 100199 |
| 04-wazuh-rule-100200.png | Full alert details for rule 100200 (frequency, MITRE, previous_output) |
| 05-thehive-alerts.png | TheHive alert list with rule-100200 tags |
| 06-thehive-case-description.png | Case #6 with description |
| 07-thehive-observables.png | Domain and source IP observables |
| 08-thehive-ttps.png | TTPs T1568.002 and T1071.004 |
| dns-sim-run.png | Running dns_sim.py on Kali (40 queries, 5-second interval) |

## Limitations

- Detection is frequency-based. It does not use entropy scoring or NXDOMAIN ratio yet.
- The lab uses private IP ranges. External enrichment (VirusTotal) cannot evaluate them, so the analyzer returned no useful result.
- The Cortex VirusTotal analyzer failed with a JSON input error (json.load(sys.stdin) received no input). The cause is suspected to be an analyzer/Cortex runtime issue, not confirmed.
- The sysmon_event10 group referenced by rule 100100 is not defined, so that rule is ignored (warning at startup).
- Cortex analysis was not verified against a real external source.

## Possible Improvements

- Add Shannon entropy scoring on the subdomain labels.
- Correlate NXDOMAIN ratio per source IP.
- Compare against passive DNS and Certificate Transparency data for real-world validation.
- Fix the sysmon_event10 group and the VirusTotal analyzer input.

## Disclaimer

Educational lab only. All domains are internal and non-routable.
