"""
Quick setup script for Windows
Checks prerequisites and guides installation
"""
import subprocess
import sys
import socket


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Error: Python 3.9+ required")
        return False
    return True


def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run(["pip", "--version"], capture_output=True, check=True)
        print("✓ pip is installed")
        return True
    except:
        print("❌ pip not found")
        return False


def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama is running")
            return True
    except:
        pass
    
    print("⚠️  Ollama not detected")
    print("   Install from: https://ollama.com/download")
    print("   Then run: ollama pull llama3.2")
    return False


def check_xmpp_server():
    """Check if XMPP server is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5222))
        sock.close()
        
        if result == 0:
            print("✓ XMPP server is running on port 5222")
            return True
    except:
        pass
    
    print("⚠️  XMPP server not detected")
    print("   Run: docker run -d -p 5222:5222 prosody/prosody")
    print("   Or install Prosody from: https://prosody.im/download/start")
    return False


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def main():
    print("=" * 60)
    print("🚨 D-MAS Emergency Response System - Setup Check")
    print("=" * 60)
    print()
    
    checks = []
    
    print("Checking prerequisites...\n")
    
    checks.append(("Python 3.9+", check_python_version()))
    checks.append(("pip", check_pip()))
    checks.append(("Ollama", check_ollama()))
    checks.append(("XMPP Server", check_xmpp_server()))
    
    print("\n" + "=" * 60)
    
    all_good = all(result for _, result in checks)
    
    if all_good:
        print("✅ All prerequisites met!")
        print("\nDo you want to install Python dependencies? (y/n): ", end="")
        
        if input().lower() == 'y':
            install_dependencies()
            
            print("\n" + "=" * 60)
            print("✅ Setup complete! You can now run:")
            print("   python main.py")
            print("=" * 60)
    else:
        print("⚠️  Some prerequisites are missing.")
        print("Please install missing components and run this script again.")
    
    print()


if __name__ == '__main__':
    main()
