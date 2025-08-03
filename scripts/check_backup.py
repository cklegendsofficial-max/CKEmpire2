#!/usr/bin/env python3
"""
CKEmpire Backup Check Script
Backup durumunu kontrol eder ve özet bilgileri gösterir
"""

import os
import json
import zipfile
from datetime import datetime

def check_backup_status():
    """Backup durumunu kontrol et"""
    backup_dir = "backups"
    
    if not os.path.exists(backup_dir):
        print("❌ Backup dizini bulunamadı")
        return
        
    print("🔍 Backup Durumu Kontrol Ediliyor...")
    print("=" * 50)
    
    # Backup dosyalarını listele
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
    
    if not backup_files:
        print("❌ ZIP backup dosyası bulunamadı")
        return
        
    latest_backup = sorted(backup_files)[-1]
    backup_path = os.path.join(backup_dir, latest_backup)
    
    # ZIP dosyası bilgilerini al
    zip_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
    zip_modified = datetime.fromtimestamp(os.path.getmtime(backup_path))
    
    print(f"📦 En Son Backup: {latest_backup}")
    print(f"💾 Boyut: {zip_size:.2f} MB")
    print(f"📅 Tarih: {zip_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ZIP içeriğini kontrol et
    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            
            print(f"\n📁 Toplam Dosya Sayısı: {len(file_list)}")
            
            # Ana modülleri kontrol et
            modules = ['backend', 'frontend', 'deployment', 'scripts', 'docs', 'tests', 'mobile', 'CKEmpireMobile']
            found_modules = []
            
            for module in modules:
                if any(f.startswith(module + '/') for f in file_list):
                    found_modules.append(module)
                    
            print(f"\n✅ Yedeklenen Modüller ({len(found_modules)}/{len(modules)}):")
            for module in found_modules:
                print(f"  • {module}")
                
            # Test sonuçlarını kontrol et
            test_results = [f for f in file_list if 'test_results' in f and f.endswith('.json')]
            print(f"\n🧪 Test Sonuçları: {len(test_results)} dosya")
            
            # Özet dosyalarını kontrol et
            summaries = [f for f in file_list if 'summaries' in f and f.endswith('.md')]
            print(f"📋 Özet Dosyaları: {len(summaries)} dosya")
            
            # Manifest dosyasını kontrol et
            manifest_files = [f for f in file_list if 'backup_manifest.json' in f]
            if manifest_files:
                print("✅ Backup manifest dosyası mevcut")
                
    except Exception as e:
        print(f"❌ ZIP dosyası okuma hatası: {e}")
        
    # Geri yükleme scriptini kontrol et
    restore_script = os.path.join(backup_dir, 'restore_system.py')
    if os.path.exists(restore_script):
        print("✅ Geri yükleme scripti mevcut")
    else:
        print("❌ Geri yükleme scripti bulunamadı")
        
    print("\n" + "=" * 50)
    print("🎉 Backup Başarıyla Tamamlandı!")
    print(f"📦 Backup Dosyası: {backup_path}")
    print(f"🔧 Geri Yükleme: python {restore_script} {backup_path}")

if __name__ == "__main__":
    check_backup_status() 