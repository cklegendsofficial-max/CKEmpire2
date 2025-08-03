#!/usr/bin/env python3
"""
CKEmpire System Restore Script
Backup'tan sistemi geri yükler
"""

import os
import sys
import zipfile
import shutil
from datetime import datetime

def restore_system(backup_zip_path):
    """Sistemi backup'tan geri yükle"""
    
    if not os.path.exists(backup_zip_path):
        print(f"❌ Backup dosyası bulunamadı: {backup_zip_path}")
        return False
        
    # Geçici dizin oluştur
    temp_dir = f"restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # ZIP'i aç
        with zipfile.ZipFile(backup_zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)
            
        # Backup manifest'ini oku
        manifest_path = os.path.join(temp_dir, 'backup_manifest.json')
        if os.path.exists(manifest_path):
            import json
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            print(f"📋 Backup bilgileri: {manifest['backup_info']['system_version']}")
            
        # Dosyaları geri yükle
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file != 'backup_manifest.json':
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, temp_dir)
                    dest_path = os.path.join('.', rel_path)
                    
                    # Dizini oluştur
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Dosyayı kopyala
                    shutil.copy2(src_path, dest_path)
                    print(f"✅ Geri yüklendi: {rel_path}")
                    
        print("🎉 Sistem başarıyla geri yüklendi!")
        return True
        
    except Exception as e:
        print(f"❌ Geri yükleme hatası: {e}")
        return False
    finally:
        # Geçici dizini temizle
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python restore_system.py <backup_zip_path>")
        sys.exit(1)
        
    backup_zip_path = sys.argv[1]
    success = restore_system(backup_zip_path)
    sys.exit(0 if success else 1)
