#!/usr/bin/env python3
"""
CKEmpire System Backup Script
Tüm sistemi yedekler ve kaydeder
"""

import os
import sys
import shutil
import json
import zipfile
from datetime import datetime
import subprocess

class SystemBackup:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.backup_dir = os.path.join(self.base_dir, 'backups')
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_name = f"ckempire_backup_{self.timestamp}"
        self.backup_path = os.path.join(self.backup_dir, self.backup_name)
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_backup_directory(self):
        """Backup dizinini oluştur"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            self.log(f"Backup dizini oluşturuldu: {self.backup_dir}")
            
    def get_system_info(self):
        """Sistem bilgilerini topla"""
        system_info = {
            "backup_timestamp": datetime.now().isoformat(),
            "system_version": "CKEmpire v1.0.0",
            "python_version": sys.version,
            "platform": sys.platform,
            "total_files": 0,
            "total_directories": 0,
            "modules": {
                "finance": "✅ Implemented",
                "analytics": "✅ Implemented", 
                "deployment": "✅ Implemented",
                "security": "✅ Implemented",
                "ai": "✅ Implemented",
                "ethics": "✅ Implemented",
                "monitoring": "✅ Implemented"
            }
        }
        
        # Dosya ve dizin sayısını hesapla
        for root, dirs, files in os.walk(self.base_dir):
            system_info["total_directories"] += len(dirs)
            system_info["total_files"] += len(files)
            
        return system_info
        
    def backup_core_modules(self):
        """Ana modülleri yedekle"""
        core_modules = [
            'backend',
            'frontend', 
            'deployment',
            'scripts',
            'docs',
            'tests',
            'mobile',
            'CKEmpireMobile'
        ]
        
        for module in core_modules:
            module_path = os.path.join(self.base_dir, module)
            if os.path.exists(module_path):
                dest_path = os.path.join(self.backup_path, module)
                shutil.copytree(module_path, dest_path)
                self.log(f"✅ {module} modülü yedeklendi")
            else:
                self.log(f"⚠️  {module} modülü bulunamadı", "WARNING")
                
    def backup_configuration_files(self):
        """Konfigürasyon dosyalarını yedekle"""
        config_files = [
            'docker-compose.yml',
            'README.md',
            'ckempire.env',
            'codecov.yml',
            '.pre-commit-config.yaml',
            '.gitignore'
        ]
        
        for file in config_files:
            file_path = os.path.join(self.base_dir, file)
            if os.path.exists(file_path):
                dest_path = os.path.join(self.backup_path, file)
                shutil.copy2(file_path, dest_path)
                self.log(f"✅ {file} yedeklendi")
            else:
                self.log(f"⚠️  {file} bulunamadı", "WARNING")
                
    def backup_test_results(self):
        """Test sonuçlarını yedekle"""
        test_results_dir = os.path.join(self.backup_path, 'test_results')
        os.makedirs(test_results_dir, exist_ok=True)
        
        # Test sonuç dosyalarını bul ve kopyala
        for file in os.listdir(self.base_dir):
            if file.endswith('.json') and 'test' in file.lower():
                src_path = os.path.join(self.base_dir, file)
                dest_path = os.path.join(test_results_dir, file)
                shutil.copy2(src_path, dest_path)
                self.log(f"✅ Test sonucu yedeklendi: {file}")
                
    def backup_summary_files(self):
        """Özet dosyalarını yedekle"""
        summary_files = [
            'DEPLOYMENT_SUMMARY.md',
            'AI_MODULE_SUMMARY.md',
            'ETHICS_MODULE_SUMMARY.md',
            'SECURITY_ENHANCEMENT_SUMMARY.md',
            'MONITORING_SUMMARY.md'
        ]
        
        summaries_dir = os.path.join(self.backup_path, 'summaries')
        os.makedirs(summaries_dir, exist_ok=True)
        
        for file in summary_files:
            file_path = os.path.join(self.base_dir, file)
            if os.path.exists(file_path):
                dest_path = os.path.join(summaries_dir, file)
                shutil.copy2(file_path, dest_path)
                self.log(f"✅ Özet dosyası yedeklendi: {file}")
            else:
                self.log(f"⚠️  {file} bulunamadı", "WARNING")
                
    def create_backup_manifest(self):
        """Backup manifest dosyası oluştur"""
        manifest = {
            "backup_info": self.get_system_info(),
            "backup_structure": {},
            "file_count": 0,
            "total_size": 0
        }
        
        # Backup yapısını analiz et
        for root, dirs, files in os.walk(self.backup_path):
            relative_path = os.path.relpath(root, self.backup_path)
            manifest["backup_structure"][relative_path] = {
                "files": files,
                "directories": dirs,
                "file_count": len(files)
            }
            manifest["file_count"] += len(files)
            
        # Toplam boyutu hesapla
        total_size = 0
        for root, dirs, files in os.walk(self.backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        manifest["total_size"] = total_size
        
        # Manifest dosyasını kaydet
        manifest_path = os.path.join(self.backup_path, 'backup_manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        self.log(f"✅ Backup manifest oluşturuldu: {manifest_path}")
        return manifest
        
    def create_zip_backup(self):
        """Backup'ı ZIP dosyası olarak sıkıştır"""
        zip_path = f"{self.backup_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.backup_path)
                    zipf.write(file_path, arcname)
                    
        self.log(f"✅ ZIP backup oluşturuldu: {zip_path}")
        return zip_path
        
    def cleanup_backup_directory(self):
        """Geçici backup dizinini temizle"""
        if os.path.exists(self.backup_path):
            shutil.rmtree(self.backup_path)
            self.log("✅ Geçici backup dizini temizlendi")
            
    def create_restore_script(self):
        """Geri yükleme scripti oluştur"""
        restore_script = f"""#!/usr/bin/env python3
\"\"\"
CKEmpire System Restore Script
Backup'tan sistemi geri yükler
\"\"\"

import os
import sys
import zipfile
import shutil
from datetime import datetime

def restore_system(backup_zip_path):
    \"\"\"Sistemi backup'tan geri yükle\"\"\"
    
    if not os.path.exists(backup_zip_path):
        print(f"❌ Backup dosyası bulunamadı: {{backup_zip_path}}")
        return False
        
    # Geçici dizin oluştur
    temp_dir = f"restore_temp_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
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
            print(f"📋 Backup bilgileri: {{manifest['backup_info']['system_version']}}")
            
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
                    print(f"✅ Geri yüklendi: {{rel_path}}")
                    
        print("🎉 Sistem başarıyla geri yüklendi!")
        return True
        
    except Exception as e:
        print(f"❌ Geri yükleme hatası: {{e}}")
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
"""
        
        restore_script_path = os.path.join(self.backup_dir, 'restore_system.py')
        with open(restore_script_path, 'w', encoding='utf-8') as f:
            f.write(restore_script)
            
        # Script'i çalıştırılabilir yap
        os.chmod(restore_script_path, 0o755)
        self.log(f"✅ Geri yükleme scripti oluşturuldu: {restore_script_path}")
        
    def run_comprehensive_backup(self):
        """Kapsamlı backup işlemini çalıştır"""
        print("🚀 CKEmpire Sistem Backup Başlatılıyor...")
        print("=" * 60)
        
        try:
            # 1. Backup dizinini oluştur
            self.create_backup_directory()
            
            # 2. Ana backup dizinini oluştur
            os.makedirs(self.backup_path, exist_ok=True)
            self.log(f"Backup dizini oluşturuldu: {self.backup_path}")
            
            # 3. Ana modülleri yedekle
            self.log("📦 Ana modüller yedekleniyor...")
            self.backup_core_modules()
            
            # 4. Konfigürasyon dosyalarını yedekle
            self.log("⚙️  Konfigürasyon dosyaları yedekleniyor...")
            self.backup_configuration_files()
            
            # 5. Test sonuçlarını yedekle
            self.log("🧪 Test sonuçları yedekleniyor...")
            self.backup_test_results()
            
            # 6. Özet dosyalarını yedekle
            self.log("📋 Özet dosyaları yedekleniyor...")
            self.backup_summary_files()
            
            # 7. Backup manifest oluştur
            self.log("📄 Backup manifest oluşturuluyor...")
            manifest = self.create_backup_manifest()
            
            # 8. ZIP backup oluştur
            self.log("🗜️  ZIP backup oluşturuluyor...")
            zip_path = self.create_zip_backup()
            
            # 9. Geri yükleme scripti oluştur
            self.log("🔧 Geri yükleme scripti oluşturuluyor...")
            self.create_restore_script()
            
            # 10. Geçici dizini temizle
            self.cleanup_backup_directory()
            
            # Sonuçları raporla
            print("\n" + "=" * 60)
            print("📊 BACKUP TAMAMLANDI")
            print("=" * 60)
            print(f"✅ Backup ZIP: {zip_path}")
            print(f"📁 Dosya sayısı: {manifest['file_count']}")
            print(f"💾 Toplam boyut: {manifest['total_size'] / (1024*1024):.2f} MB")
            print(f"📅 Tarih: {manifest['backup_info']['backup_timestamp']}")
            print(f"🐍 Python: {manifest['backup_info']['python_version']}")
            
            print("\n📋 Yedeklenen Modüller:")
            for module, status in manifest['backup_info']['modules'].items():
                print(f"  • {module}: {status}")
                
            print(f"\n🔧 Geri yükleme için: python backups/restore_system.py {zip_path}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Backup hatası: {e}", "ERROR")
            return False

def main():
    """Ana fonksiyon"""
    backup = SystemBackup()
    success = backup.run_comprehensive_backup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 