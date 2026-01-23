# pymodules/disavow_service.py
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

import re
import uuid

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from config import Config


IP_PATTERN = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')


class DisavowService:

    def __init__(self):
        self.input_dir = Config.INPUT_FOLDER
        self.output_dir = Config.OUTPUT_FOLDER
        self.whitelist_file = Config.WHITELIST_FILE

    def get_stats(self) -> dict:
        input_files = list(self.input_dir.glob("*.xlsx")) + \
                      list(self.input_dir.glob("*.xls")) + \
                      list(self.input_dir.glob("*.csv")) + \
                      list(self.input_dir.glob("*.txt"))

        output_files = list(self.output_dir.glob("disavow_*.txt"))

        previous = self._load_previous_disavows()

        whitelist = self.get_whitelist()

        return {
            "input_files": len(input_files),
            "output_files": len(output_files),
            "total_ips": len(previous["ips"]),
            "total_domains": len(previous["domains"]),
            "total_urls": len(previous["urls"]),
            "whitelist_count": len(whitelist),
            "last_output": self._get_last_output_info()
        }

    def _get_last_output_info(self) -> dict | None:
        output_files = sorted(self.output_dir.glob("disavow_*.txt"), reverse=True)
        if output_files:
            last_file = output_files[0]
            stat = last_file.stat()
            return {
                "filename": last_file.name,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size
            }
        return None

    def get_whitelist(self) -> list:
        whitelist = []
        if self.whitelist_file.exists():
            with open(self.whitelist_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        whitelist.append(line.lower().replace("www.", ""))
        return sorted(set(whitelist))

    def save_whitelist(self, domains: list):
        header = """# Domains Whitelist - Disavow Generator
# Add a domain per line (without http:// or www.)
# Lines starting with # are comments

"""
        with open(self.whitelist_file, "w", encoding="utf-8") as f:
            f.write(header)
            for domain in sorted(set(domains)):
                if domain.strip():
                    f.write(f"{domain.strip().lower()}\n")

    def add_to_whitelist(self, domain: str):
        whitelist = self.get_whitelist()
        domain = domain.strip().lower().replace("www.", "")
        if domain and domain not in whitelist:
            whitelist.append(domain)
            self.save_whitelist(whitelist)

    def list_input_files(self) -> list:
        files = []
        for ext in ["xlsx", "xls", "csv", "txt"]:
            for f in self.input_dir.glob(f"*.{ext}"):
                stat = f.stat()
                files.append({
                    "name": f.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": ext.upper()
                })
        return sorted(files, key=lambda x: x["modified"], reverse=True)

    def list_output_files(self) -> list:
        files = []
        for f in self.output_dir.glob("disavow_*.txt"):
            stat = f.stat()
            stats = self._parse_disavow_stats(f)
            files.append({
                "name": f.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                **stats
            })
        return sorted(files, key=lambda x: x["created"], reverse=True)

    def _parse_disavow_stats(self, filepath: Path) -> dict:
        stats = {"ips": 0, "domains": 0, "urls": 0}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#   - IPs:"):
                        stats["ips"] = int(line.split(":")[1].strip())
                    elif line.startswith("#   - Domains:"):
                        stats["domains"] = int(line.split(":")[1].strip())
                    elif line.startswith("#   - Specific URLs:"):
                        stats["urls"] = int(line.split(":")[1].strip())
                    elif not line.startswith("#"):
                        break
        except Exception:
            pass
        return stats

    def process_files(self) -> dict:
        whitelist = set(self.get_whitelist())

        previous = self._load_previous_disavows()

        all_urls = self._read_input_files()

        if not all_urls:
            return {
                "success": False,
                "error": "No URLs found in input files"
            }

        categorized = self._categorize_urls(all_urls, whitelist)

        new_entries = {
            "ips": sorted(set(categorized["ips"]) - previous["ips"]),
            "domains": sorted(set(categorized["domains"]) - previous["domains"]),
            "urls": sorted(set(categorized["urls"]) - previous["urls"])
        }

        output_file = self._generate_disavow_file(categorized)

        return {
            "success": True,
            "filename": Path(output_file).name,
            "total_urls_processed": len(all_urls),
            "stats": {
                "ips": len(categorized["ips"]),
                "domains": len(categorized["domains"]),
                "urls": len(categorized["urls"]),
                "total": len(categorized["ips"]) + len(categorized["domains"]) + len(categorized["urls"])
            },
            "new_entries": {
                "ips": len(new_entries["ips"]),
                "domains": len(new_entries["domains"]),
                "urls": len(new_entries["urls"]),
                "total": len(new_entries["ips"]) + len(new_entries["domains"]) + len(new_entries["urls"]),
                "list": {
                    "ips": new_entries["ips"],
                    "domains": new_entries["domains"],
                    "urls": new_entries["urls"]
                }
            }
        }

    def _read_input_files(self) -> list:
        all_urls = []

        for excel_file in list(self.input_dir.glob("*.xlsx")) + list(self.input_dir.glob("*.xls")):
            try:
                df = pd.read_excel(excel_file)
                urls = self._extract_urls_from_dataframe(df)
                all_urls.extend(urls)
            except Exception:
                continue

        for csv_file in self.input_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                urls = self._extract_urls_from_dataframe(df)
                all_urls.extend(urls)
            except Exception:
                continue

        url_pattern = re.compile(r'https?://[^\s<>"\')\]]+')
        for txt_file in self.input_dir.glob("*.txt"):
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if line.lower().startswith("domain:"):
                            domain = line[7:].strip()
                            if "." in domain:
                                all_urls.append(f"http://{domain}/")
                        else:
                            found_urls = url_pattern.findall(line)
                            all_urls.extend(found_urls)
            except Exception:
                continue

        return all_urls

    def _extract_urls_from_dataframe(self, df) -> list:
        url_column = None
        for col in df.columns:
            col_lower = str(col).lower()
            if any(kw in col_lower for kw in ["link", "url", "página", "pagina", "enlace", "source"]):
                url_column = col
                break

        if url_column is None:
            url_column = df.columns[0]

        return df[url_column].dropna().astype(str).tolist()

    def _categorize_urls(self, urls: list, whitelist: set) -> dict:
        ips = set()
        domains = set()
        specific_urls = set()

        for url in urls:
            url = url.strip()
            if not url:
                continue

            tipo, valor = self._extract_domain_or_ip(url)

            if tipo is None:
                continue

            if self._is_whitelisted(valor, whitelist):
                continue

            if tipo == "ip":
                ips.add(valor)
            elif tipo == "domain":
                domains.add(valor)
            else:
                specific_urls.add(url)

        return {
            "ips": sorted(ips),
            "domains": sorted(domains),
            "urls": sorted(specific_urls)
        }

    def _extract_domain_or_ip(self, url: str) -> tuple:
        try:
            if not url.startswith(("http://", "https://")):
                url = "http://" + url

            parsed = urlparse(url)
            host = parsed.netloc.lower()

            if ":" in host:
                host = host.split(":")[0]

            if not host or "." not in host:
                return (None, None)

            if IP_PATTERN.match(host):
                return ("ip", host)

            domain = host.replace("www.", "")
            return ("domain", domain)

        except Exception:
            return (None, None)

    def _is_whitelisted(self, domain_or_ip: str, whitelist: set) -> bool:
        normalized = domain_or_ip.lower().replace("www.", "")

        if normalized in whitelist:
            return True

        for wl_domain in whitelist:
            if normalized.endswith("." + wl_domain):
                return True

        return False

    def _load_previous_disavows(self) -> dict:
        previous = {"ips": set(), "domains": set(), "urls": set()}

        for disavow_file in self.output_dir.glob("disavow_*.txt"):
            try:
                with open(disavow_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue

                        if line.startswith("domain:"):
                            target = line[7:]
                            if IP_PATTERN.match(target):
                                previous["ips"].add(target)
                            else:
                                previous["domains"].add(target.lower())
                        elif line.startswith("http"):
                            previous["urls"].add(line)
            except Exception:
                continue

        return previous

    def _generate_disavow_file(self, categorized: dict) -> str:
        uuid8 = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"disavow_{uuid8}_{timestamp}.txt"
        filepath = self.output_dir / filename

        total_entries = len(categorized["ips"]) + len(categorized["domains"]) + len(categorized["urls"])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Disavow File - Generated by Disavow Generator\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total entries: {total_entries}\n")
            f.write(f"#   - IPs: {len(categorized['ips'])}\n")
            f.write(f"#   - Domains: {len(categorized['domains'])}\n")
            f.write(f"#   - Specific URLs: {len(categorized['urls'])}\n")
            f.write("#\n")
            f.write("# Upload this file to Google Search Console:\n")
            f.write("# https://search.google.com/search-console/disavow-links\n")
            f.write("\n")

            if categorized["ips"]:
                f.write("# ============================================\n")
                f.write("# IPs\n")
                f.write("# ============================================\n")
                for ip in categorized["ips"]:
                    f.write(f"domain:{ip}\n")
                f.write("\n")

            if categorized["domains"]:
                f.write("# ============================================\n")
                f.write("# DOMAINS\n")
                f.write("# ============================================\n")
                for domain in categorized["domains"]:
                    f.write(f"domain:{domain}\n")
                f.write("\n")

            if categorized["urls"]:
                f.write("# ============================================\n")
                f.write("# SPECIFIC URLs\n")
                f.write("# ============================================\n")
                for url in categorized["urls"]:
                    f.write(f"{url}\n")

        return str(filepath)
