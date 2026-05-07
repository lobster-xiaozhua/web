import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.search_service import _es_search


class TestEsSearch:
    @pytest.mark.asyncio
    async def test_es_search_basic(self):
        mock_client = AsyncMock()
        mock_result = {
            "hits": {
                "hits": [
                    {
                        "_id": "test-id-1",
                        "_score": 10.5,
                        "_source": {
                            "title": "测试小说",
                            "author": "测试作者",
                            "category": "玄幻",
                            "description": "测试描述",
                        },
                        "highlight": {"title": ["<em>测试</em>小说"]},
                    }
                ]
            }
        }
        mock_client.search = AsyncMock(return_value=mock_result)

        results = await _es_search(mock_client, "测试", size=20)

        assert len(results) == 1
        assert results[0]["id"] == "test-id-1"
        assert results[0]["score"] == 10.5
        assert results[0]["source"]["title"] == "测试小说"
        assert results[0]["highlight"]["title"] == ["<em>测试</em>小说"]

    @pytest.mark.asyncio
    async def test_es_search_empty_results(self):
        mock_client = AsyncMock()
        mock_result = {"hits": {"hits": []}}
        mock_client.search = AsyncMock(return_value=mock_result)

        results = await _es_search(mock_client, "不存在的关键词", size=20)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_es_search_multiple_results(self):
        mock_client = AsyncMock()
        mock_result = {
            "hits": {
                "hits": [
                    {
                        "_id": "id-1",
                        "_score": 15.0,
                        "_source": {"title": "小说1", "author": "作者1", "category": "玄幻", "description": ""},
                        "highlight": {},
                    },
                    {
                        "_id": "id-2",
                        "_score": 10.0,
                        "_source": {"title": "小说2", "author": "作者2", "category": "科幻", "description": ""},
                        "highlight": {},
                    },
                ]
            }
        }
        mock_client.search = AsyncMock(return_value=mock_result)

        results = await _es_search(mock_client, "小说", size=20)

        assert len(results) == 2
        assert results[0]["id"] == "id-1"
        assert results[1]["id"] == "id-2"

    @pytest.mark.asyncio
    async def test_es_search_handles_missing_highlight(self):
        mock_client = AsyncMock()
        mock_result = {
            "hits": {
                "hits": [
                    {
                        "_id": "id-1",
                        "_score": 10.0,
                        "_source": {"title": "小说", "author": "作者", "category": "玄幻", "description": ""},
                    }
                ]
            }
        }
        mock_client.search = AsyncMock(return_value=mock_result)

        results = await _es_search(mock_client, "小说", size=20)

        assert len(results) == 1
        assert results[0]["highlight"] == {}

    @pytest.mark.asyncio
    async def test_es_search_fields_extraction(self):
        mock_client = AsyncMock()
        mock_result = {
            "hits": {
                "hits": [
                    {
                        "_id": "test-uuid",
                        "_score": 25.0,
                        "_source": {
                            "title": "Extracted Title",
                            "author": "Extracted Author",
                            "category": "Action",
                            "description": "A great story",
                        },
                        "highlight": {"description": ["A <em>great</em> story"]},
                    }
                ]
            }
        }
        mock_client.search = AsyncMock(return_value=mock_result)

        results = await _es_search(mock_client, "great", size=10)

        assert len(results) == 1
        assert results[0]["source"]["title"] == "Extracted Title"
        assert results[0]["source"]["author"] == "Extracted Author"
        assert results[0]["source"]["category"] == "Action"
