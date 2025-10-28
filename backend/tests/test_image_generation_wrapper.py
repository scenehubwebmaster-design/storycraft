import asyncio


def test_generate_landscape_calls_sd_client(monkeypatch):
    """Ensure generate_landscape_image invokes the StableDiffusion client with expected fields."""
    container = {}

    class FakeClient:
        def __init__(self):
            # expose instance to test
            container['inst'] = self

        def generate_image(self, **kwargs):
            # record the kwargs and return a minimal fake image
            self.kwargs = kwargs
            return {'image': 'fake_base64_data'}

    # Patch the StableDiffusionClient class in the stablediffusion_client module
    import backend.stablediffusion_client as sdmod

    monkeypatch.setattr(sdmod, 'StableDiffusionClient', FakeClient)

    # Now import the helper and call it
    from backend.image_generation import generate_landscape_image

    # Run the coroutine
    res = asyncio.get_event_loop().run_until_complete(
        generate_landscape_image("A lonely lighthouse on a cliff, dramatic sky", provider="stablediffusion", style="cinematic")
    )

    # Verify the fake client was used and called with expected keys
    inst = container.get('inst')
    assert inst is not None, "StableDiffusionClient was not constructed"
    assert hasattr(inst, 'kwargs'), "generate_image was not called on the client"

    kwargs = inst.kwargs
    # Basic expectations
    assert 'prompt' in kwargs and isinstance(kwargs['prompt'], str)
    assert 'negative_prompt' in kwargs and isinstance(kwargs['negative_prompt'], str)
    assert 'steps' in kwargs and kwargs['steps'] == 30
    assert 'cfg_scale' in kwargs and kwargs['cfg_scale'] == 7.5
    assert 'width' in kwargs and 'height' in kwargs
    assert 'seed' in kwargs

    # Ensure style descriptor appears in the prompt
    assert 'cinematic' in kwargs['prompt'].lower()

    # And ensure the wrapper returned the fake image
    assert res.get('image_base64') == 'fake_base64_data'
