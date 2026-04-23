import pytest
from unittest.mock import patch, MagicMock
from src.ai_dj import AIDJ

@pytest.fixture
def sample_songs():
    return [
        {"id": 1, "title": "Rock Anthem", "artist": "The Rocks", "genre": "rock", "mood": "intense", "energy": 0.9},
        {"id": 2, "title": "Chill Beats", "artist": "LoFi King", "genre": "lofi", "mood": "calm", "energy": 0.2},
        {"id": 3, "title": "Pop Hit", "artist": "Pop Star", "genre": "pop", "mood": "happy", "energy": 0.7}
    ]

@patch("src.ai_dj.SentenceTransformer")
@patch("src.ai_dj.cosine_similarity")
def test_retrieval(mock_cosine, mock_st, sample_songs):
    # Mocking the embedding model
    mock_model_instance = MagicMock()
    mock_model_instance.encode.return_value = [[0.1, 0.2]] # Dummy embedding
    mock_st.return_value = mock_model_instance
    
    # Mocking similarity so the second song is always the closest
    mock_cosine.return_value = [[0.1, 0.9, 0.3]]
    
    dj = AIDJ(sample_songs)
    
    # Run retrieval
    results = dj.retrieve("I want something chill", k=1)
    
    # Ensure it returns the 2nd song due to mock
    assert len(results) == 1
    assert results[0][0]["title"] == "Chill Beats"
    assert results[0][1] == 0.9

@patch("src.ai_dj.SentenceTransformer")
def test_generation_fallback_no_api_key(mock_st, sample_songs):
    # If no API key is provided, the DJ should fallback gracefully
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'your_api_key_here'}):
        dj = AIDJ(sample_songs)
        assert dj.generation_ready == False
        
        # Should return a string stating it skipped generation
        retrieved_mock = [(sample_songs[0], 0.8)]
        response = dj.generate("test prompt", retrieved_mock)
        assert "Generation Skipped" in response
        assert "Rock Anthem" in response
