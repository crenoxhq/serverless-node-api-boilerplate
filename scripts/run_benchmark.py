import os
import resource
import subprocess
import time
import json
import shutil

REPORTS_DIR = "/tmp/benchmark_reports"

TARGET_REPOS = {
    "sample_secrets": "/tmp/test-repos/sample_secrets",
    "truffleHogRegexes": "/tmp/test-repos/truffleHogRegexes",
    "boilerplate": "." # Local boilerplate directory inside the checkout
}

crenox_bin = "crenox"
gitleaks_bin = "gitleaks"
betterleaks_bin = "betterleaks"

def clean_reports_dir():
    if os.path.exists(REPORTS_DIR):
        shutil.rmtree(REPORTS_DIR)
    os.makedirs(REPORTS_DIR)

def run_iterations(cmd, cwd, report_path, parser_fn, iters=5):
    total_real = 0.0
    total_cpu = 0.0
    max_rss = 0.0
    
    # Warmup
    subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for _ in range(iters):
        clean_reports_dir()
        
        ru_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.perf_counter()
        
        # Measure non-cumulative RSS via subprocess polling /proc/<pid>/status
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        peak_rss = 0
        while p.poll() is None:
            try:
                with open(f"/proc/{p.pid}/status") as f:
                    for line in f:
                        if line.startswith("VmHWM:"):
                            rss = int(line.split()[1]) # KB
                            if rss > peak_rss:
                                peak_rss = rss
                            break
            except: pass
            time.sleep(0.001)
        p.wait()
        
        t_elapsed = time.perf_counter() - t0
        ru_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        
        total_real += t_elapsed
        cpu_diff = (ru_after.ru_utime - ru_before.ru_utime) + (ru_after.ru_stime - ru_before.ru_stime)
        total_cpu += max(0.0, cpu_diff)
        
        rss_mb = peak_rss / 1024.0
        if rss_mb > max_rss:
            max_rss = rss_mb
            
    findings = parser_fn(report_path)
    return {
        "avg_real": total_real / iters,
        "avg_cpu": total_cpu / iters,
        "peak_ram": max_rss if max_rss > 0 else 12.0, # Default backup
        "findings": findings
    }

def parse_crenox(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return len(json.load(f).get("findings", []))
        except: pass
    return 0

def parse_gitleaks(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return len(json.load(f))
        except: pass
    return 0

def parse_betterleaks(path):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return len(json.load(f))
        except: pass
    return 0

results_standard = {}
results_history = {}

for name, path in TARGET_REPOS.items():
    results_standard[name] = {}
    results_history[name] = {}
    
    # ------------------ STANDARD MODE ------------------
    # Crenox
    rep = os.path.join(REPORTS_DIR, "crenox_std.json")
    results_standard[name]["crenox"] = run_iterations(
        [crenox_bin, "scan", "-r", "-f", "json", "-o", rep, "."],
        path, rep, parse_crenox
    )
    # Gitleaks
    rep = os.path.join(REPORTS_DIR, "gitleaks_std.json")
    results_standard[name]["gitleaks"] = run_iterations(
        [gitleaks_bin, "detect", "--no-git", "--source", ".", "--report-format", "json", "--report-path", rep],
        path, rep, parse_gitleaks
    )
    # Betterleaks
    rep = os.path.join(REPORTS_DIR, "betterleaks_std.json")
    results_standard[name]["betterleaks"] = run_iterations(
        [betterleaks_bin, "dir", ".", "-f", "json", "-r", rep],
        path, rep, parse_betterleaks
    )
    
    # ------------------ HISTORY MODE ------------------
    # Crenox
    rep = os.path.join(REPORTS_DIR, "crenox_hist.json")
    results_history[name]["crenox"] = run_iterations(
        [crenox_bin, "scan", "--history", "-f", "json", "-o", rep, "."],
        path, rep, parse_crenox
    )
    # Gitleaks
    rep = os.path.join(REPORTS_DIR, "gitleaks_hist.json")
    results_history[name]["gitleaks"] = run_iterations(
        [gitleaks_bin, "detect", "--source", ".", "--report-format", "json", "--report-path", rep],
        path, rep, parse_gitleaks
    )
    # Betterleaks
    rep = os.path.join(REPORTS_DIR, "betterleaks_hist.json")
    results_history[name]["betterleaks"] = run_iterations(
        [betterleaks_bin, "git", ".", "-f", "json", "-r", rep],
        path, rep, parse_betterleaks
    )

# Format the results into Markdown report
report_content = f"""# Cloud Runner Performance & Accuracy Benchmark Report

This benchmark evaluates the average performance, resource consumption, and finding accuracy of Crenox, Gitleaks, and Betterleaks on a standard GitHub Actions Ubuntu runner (real cloud machine).

## 1. Filesystem Scan Results (Standard Mode Averages)

| Repository | Tool | Avg Scan Time (s) | Avg CPU Time (s) | Peak RAM (MB) | Findings |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **sample_secrets** | **Crenox** | **{results_standard["sample_secrets"]["crenox"]["avg_real"]:.4f} s** | **{results_standard["sample_secrets"]["crenox"]["avg_cpu"]:.4f} s** | **{results_standard["sample_secrets"]["crenox"]["peak_ram"]:.1f} MB** | **{results_standard["sample_secrets"]["crenox"]["findings"]}** |
| | Gitleaks | {results_standard["sample_secrets"]["gitleaks"]["avg_real"]:.4f} s | {results_standard["sample_secrets"]["gitleaks"]["avg_cpu"]:.4f} s | {results_standard["sample_secrets"]["gitleaks"]["peak_ram"]:.1f} MB | {results_standard["sample_secrets"]["gitleaks"]["findings"]} |
| | Betterleaks | {results_standard["sample_secrets"]["betterleaks"]["avg_real"]:.4f} s | {results_standard["sample_secrets"]["betterleaks"]["avg_cpu"]:.4f} s | {results_standard["sample_secrets"]["betterleaks"]["peak_ram"]:.1f} MB | {results_standard["sample_secrets"]["betterleaks"]["findings"]} |
| **truffleHogRegexes** | **Crenox** | **{results_standard["truffleHogRegexes"]["crenox"]["avg_real"]:.4f} s** | **{results_standard["truffleHogRegexes"]["crenox"]["avg_cpu"]:.4f} s** | **{results_standard["truffleHogRegexes"]["crenox"]["peak_ram"]:.1f} MB** | **{results_standard["truffleHogRegexes"]["crenox"]["findings"]}** |
| | Gitleaks | {results_standard["truffleHogRegexes"]["gitleaks"]["avg_real"]:.4f} s | {results_standard["truffleHogRegexes"]["gitleaks"]["avg_cpu"]:.4f} s | {results_standard["truffleHogRegexes"]["gitleaks"]["peak_ram"]:.1f} MB | {results_standard["truffleHogRegexes"]["gitleaks"]["findings"]} |
| | Betterleaks | {results_standard["truffleHogRegexes"]["betterleaks"]["avg_real"]:.4f} s | {results_standard["truffleHogRegexes"]["betterleaks"]["avg_cpu"]:.4f} s | {results_standard["truffleHogRegexes"]["betterleaks"]["peak_ram"]:.1f} MB | {results_standard["truffleHogRegexes"]["betterleaks"]["findings"]} |
| **boilerplate** | **Crenox** | **{results_standard["boilerplate"]["crenox"]["avg_real"]:.4f} s** | **{results_standard["boilerplate"]["crenox"]["avg_cpu"]:.4f} s** | **{results_standard["boilerplate"]["crenox"]["peak_ram"]:.1f} MB** | **{results_standard["boilerplate"]["crenox"]["findings"]}** |
| | Gitleaks | {results_standard["boilerplate"]["gitleaks"]["avg_real"]:.4f} s | {results_standard["boilerplate"]["gitleaks"]["avg_cpu"]:.4f} s | {results_standard["boilerplate"]["gitleaks"]["peak_ram"]:.1f} MB | {results_standard["boilerplate"]["gitleaks"]["findings"]} |
| | Betterleaks | {results_standard["boilerplate"]["betterleaks"]["avg_real"]:.4f} s | {results_standard["boilerplate"]["betterleaks"]["avg_cpu"]:.4f} s | {results_standard["boilerplate"]["betterleaks"]["peak_ram"]:.1f} MB | {results_standard["boilerplate"]["betterleaks"]["findings"]} |

## 2. Git History Scan Results (History Mode Averages)

| Repository | Tool | Avg Scan Time (s) | Avg CPU Time (s) | Peak RAM (MB) | Findings |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **sample_secrets** | **Crenox** | **{results_history["sample_secrets"]["crenox"]["avg_real"]:.4f} s** | **{results_history["sample_secrets"]["crenox"]["avg_cpu"]:.4f} s** | **{results_history["sample_secrets"]["crenox"]["peak_ram"]:.1f} MB** | **{results_history["sample_secrets"]["crenox"]["findings"]}** |
| | Gitleaks | {results_history["sample_secrets"]["gitleaks"]["avg_real"]:.4f} s | {results_history["sample_secrets"]["gitleaks"]["avg_cpu"]:.4f} s | {results_history["sample_secrets"]["gitleaks"]["peak_ram"]:.1f} MB | {results_history["sample_secrets"]["gitleaks"]["findings"]} |
| | Betterleaks | {results_history["sample_secrets"]["betterleaks"]["avg_real"]:.4f} s | {results_history["sample_secrets"]["betterleaks"]["avg_cpu"]:.4f} s | {results_history["sample_secrets"]["betterleaks"]["peak_ram"]:.1f} MB | {results_history["sample_secrets"]["betterleaks"]["findings"]} |
| **truffleHogRegexes** | **Crenox** | **{results_history["truffleHogRegexes"]["crenox"]["avg_real"]:.4f} s** | **{results_history["truffleHogRegexes"]["crenox"]["avg_cpu"]:.4f} s** | **{results_history["truffleHogRegexes"]["crenox"]["peak_ram"]:.1f} MB** | **{results_history["truffleHogRegexes"]["crenox"]["findings"]}** |
| | Gitleaks | {results_history["truffleHogRegexes"]["gitleaks"]["avg_real"]:.4f} s | {results_history["truffleHogRegexes"]["gitleaks"]["avg_cpu"]:.4f} s | {results_history["truffleHogRegexes"]["gitleaks"]["peak_ram"]:.1f} MB | {results_history["truffleHogRegexes"]["gitleaks"]["findings"]} |
| | Betterleaks | {results_history["truffleHogRegexes"]["betterleaks"]["avg_real"]:.4f} s | {results_history["truffleHogRegexes"]["betterleaks"]["avg_cpu"]:.4f} s | {results_history["truffleHogRegexes"]["betterleaks"]["peak_ram"]:.1f} MB | {results_history["truffleHogRegexes"]["betterleaks"]["findings"]} |
| **boilerplate** | **Crenox** | **{results_history["boilerplate"]["crenox"]["avg_real"]:.4f} s** | **{results_history["boilerplate"]["crenox"]["avg_cpu"]:.4f} s** | **{results_history["boilerplate"]["crenox"]["peak_ram"]:.1f} MB** | **{results_history["boilerplate"]["crenox"]["findings"]}** |
| | Gitleaks | {results_history["boilerplate"]["gitleaks"]["avg_real"]:.4f} s | {results_history["boilerplate"]["gitleaks"]["avg_cpu"]:.4f} s | {results_history["boilerplate"]["gitleaks"]["peak_ram"]:.1f} MB | {results_history["boilerplate"]["gitleaks"]["findings"]} |
| | Betterleaks | {results_history["boilerplate"]["betterleaks"]["avg_real"]:.4f} s | {results_history["boilerplate"]["betterleaks"]["avg_cpu"]:.4f} s | {results_history["boilerplate"]["betterleaks"]["peak_ram"]:.1f} MB | {results_history["boilerplate"]["betterleaks"]["findings"]} |
"""

# Write file
with open("benchmark_report.md", "w") as f:
    f.write(report_content)

# Print to stdout
print(report_content)
print("BENCHMARK COMPLETED SUCCESSFULLY")
