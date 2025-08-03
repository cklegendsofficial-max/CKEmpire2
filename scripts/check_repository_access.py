#!/usr/bin/env python3
"""
CKEmpire Repository Access Check Script
Repository erişim sorunlarını kontrol eder
"""

import requests
import json
import subprocess
import sys
from datetime import datetime

def check_repository_access():
    """Repository erişim durumunu kontrol et"""
    
    print("🔍 CKEmpire Repository Erişim Kontrolü")
    print("=" * 60)
    
    # Repository bilgileri
    repo_owner = "cklegendsofficial-max"
    repo_name = "CKEmpire"
    repo_url = f"https://github.com/{repo_owner}/{repo_name}"
    
    print(f"📦 Repository: {repo_url}")
    print(f"👤 Owner: {repo_owner}")
    print(f"📁 Name: {repo_name}")
    
    # 1. Repository'nin var olup olmadığını kontrol et
    print("\n1️⃣ Repository Varlık Kontrolü...")
    try:
        response = requests.get(repo_url, timeout=10)
        if response.status_code == 200:
            print("✅ Repository erişilebilir")
        elif response.status_code == 404:
            print("❌ Repository bulunamadı (404)")
            return False
        else:
            print(f"⚠️  Beklenmeyen durum kodu: {response.status_code}")
    except Exception as e:
        print(f"❌ Repository erişim hatası: {e}")
        return False
    
    # 2. Git remote URL'ini kontrol et
    print("\n2️⃣ Git Remote URL Kontrolü...")
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, check=True
        )
        remote_url = result.stdout.strip()
        print(f"✅ Remote URL: {remote_url}")
        
        # URL formatını kontrol et
        if "github.com" in remote_url:
            print("✅ GitHub URL formatı doğru")
        else:
            print("⚠️  GitHub URL formatı beklenmeyen")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git remote URL hatası: {e}")
        return False
    
    # 3. Repository'nin public/private durumunu kontrol et
    print("\n3️⃣ Repository Görünürlük Kontrolü...")
    try:
        # GitHub API ile repository bilgilerini al
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            repo_data = response.json()
            visibility = repo_data.get("private", True)
            if visibility:
                print("🔒 Repository PRIVATE - Erişim kısıtlı")
                print("💡 Çözüm: Repository'yi PUBLIC yapın")
                return False
            else:
                print("🌐 Repository PUBLIC - Erişim açık")
        elif response.status_code == 404:
            print("❌ Repository API'de bulunamadı")
            return False
        else:
            print(f"⚠️  API durum kodu: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API erişim hatası: {e}")
        return False
    
    # 4. Repository içeriğini kontrol et
    print("\n4️⃣ Repository İçerik Kontrolü...")
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, check=True
        )
        latest_commit = result.stdout.strip()
        print(f"✅ Son commit: {latest_commit}")
        
        # Dosya sayısını kontrol et
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, check=True
        )
        file_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        print(f"📁 Dosya sayısı: {file_count}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git içerik kontrolü hatası: {e}")
        return False
    
    # 5. Branch durumunu kontrol et
    print("\n5️⃣ Branch Durumu Kontrolü...")
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True
        )
        current_branch = result.stdout.strip()
        print(f"✅ Aktif branch: {current_branch}")
        
        # Remote ile senkronizasyon kontrolü
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            print("✅ Working tree temiz")
        else:
            print("⚠️  Commit edilmemiş değişiklikler var")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Branch kontrolü hatası: {e}")
        return False
    
    # 6. Erişim sorunları ve çözümler
    print("\n6️⃣ Olası Erişim Sorunları ve Çözümler...")
    
    issues = []
    solutions = []
    
    # Repository private olabilir
    try:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            if repo_data.get("private", True):
                issues.append("Repository PRIVATE")
                solutions.append("GitHub'da repository ayarlarından 'Make public' seçeneğini kullanın")
    except:
        pass
    
    # URL formatı sorunu olabilir
    if "cklegendsofficial-max" not in repo_url:
        issues.append("Repository URL formatı yanlış")
        solutions.append("Doğru URL: https://github.com/cklegendsofficial-max/CKEmpire")
    
    # Repository boş olabilir
    try:
        result = subprocess.run(
            ["git", "log", "--oneline"],
            capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            issues.append("Repository boş")
            solutions.append("İlk commit'i yapın")
    except:
        pass
    
    if issues:
        print("❌ Tespit edilen sorunlar:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n💡 Çözüm önerileri:")
        for i, solution in enumerate(solutions, 1):
            print(f"  {i}. {solution}")
    else:
        print("✅ Erişim sorunu tespit edilmedi")
    
    # 7. Test URL'leri
    print("\n7️⃣ Test URL'leri...")
    test_urls = [
        f"https://github.com/{repo_owner}/{repo_name}",
        f"https://github.com/{repo_owner}/{repo_name}.git",
        f"git@github.com:{repo_owner}/{repo_name}.git"
    ]
    
    for url in test_urls:
        print(f"🔗 {url}")
    
    print("\n" + "=" * 60)
    print("📋 Özet")
    print("=" * 60)
    
    if not issues:
        print("✅ Repository erişime hazır")
        print(f"🌐 Public URL: {repo_url}")
        print("🔗 Diğer yapay zekalar bu URL'yi kullanabilir")
    else:
        print("❌ Repository erişim sorunları var")
        print("🔧 Yukarıdaki çözümleri uygulayın")
    
    return len(issues) == 0

def main():
    """Ana fonksiyon"""
    success = check_repository_access()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 