"""
Test Stable Diffusion integration
"""
from .stablediffusion_client import StableDiffusionClient, generate_portrait_with_sd

def test_connection():
    """Test if SD server is reachable"""
    client = StableDiffusionClient()
    if client.test_connection():
        print("✅ Successfully connected to Stable Diffusion server")
        return True
    else:
        print("❌ Failed to connect to Stable Diffusion server")
        print(f"   Make sure server is running at {client.base_url}")
        return False

def test_generate_portrait():
    """Test portrait generation"""
    print("\n🎨 Testing portrait generation...")
    
    try:
        image_base64, prompt = generate_portrait_with_sd(
            character_description="a young elf warrior with long blonde hair and piercing blue eyes",
            style="fantasy",
            quality="draft"  # Use draft for faster testing
        )
        
        print("✅ Portrait generated successfully!")
        print(f"   Prompt: {prompt[:100]}...")
        print(f"   Image size: {len(image_base64)} characters")
        
        # Optionally save to file for inspection
        import base64
        with open("test_portrait.png", "wb") as f:
            f.write(base64.b64decode(image_base64))
        print("   Saved to test_portrait.png")
        
        return True
    except Exception as e:
        print(f"❌ Portrait generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Stable Diffusion Integration\n")
    print("=" * 50)
    
    # Test connection
    if not test_connection():
        print("\n⚠️  Cannot proceed with generation test - server not reachable")
        exit(1)
    
    # Test generation
    test_generate_portrait()
    
    print("\n" + "=" * 50)
    print("✨ Tests complete!")
