"""Tests for input sanitization and XSS prevention."""

import pytest


@pytest.mark.anyio
async def test_create_task_xss_script_tag_blocked(client):
    """Test that <script> tags are stripped from title."""
    xss_payload = "<script>alert(1)</script>"
    expected_cleaned = "alert(1)"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": xss_payload, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == expected_cleaned
    assert "<script>" not in data["title"]


@pytest.mark.anyio
async def test_create_task_xss_img_onerror_blocked(client):
    """Test that image onerror attributes are stripped from title."""
    xss_payload = '<img onerror=alert(1) src=x>'

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": xss_payload, "description": "Test task"}
    )

    # The title becomes empty after stripping HTML, so it should be rejected
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_task_xss_body_onload_blocked(client):
    """Test that body onload attributes are stripped from title."""
    xss_payload = '<body onload=alert(1)>Test Content</body>'
    expected_cleaned = "Test Content"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": xss_payload, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == expected_cleaned


@pytest.mark.anyio
async def test_create_task_xss_iframe_javascript_blocked(client):
    """Test that iframe javascript URLs are stripped from title."""
    xss_payload = '<iframe src="javascript:alert(1)">'

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": xss_payload, "description": "Test task"}
    )

    # Title becomes empty after stripping
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_task_html_bold_tags_stripped(client):
    """Test that HTML formatting tags are stripped (not rendered)."""
    html_payload = "<b>bold</b> and <i>italic</i> text"
    expected_cleaned = "bold and italic text"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": html_payload, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == expected_cleaned


@pytest.mark.anyio
async def test_create_task_empty_title_rejected(client):
    """Test that empty title is rejected with 422."""
    resp = await client.post(
        "/api/v1/tasks",
        json={"title": "", "description": "Test task"}
    )

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_task_whitespace_only_title_rejected(client):
    """Test that whitespace-only title is rejected (becomes empty after stripping)."""
    resp = await client.post(
        "/api/v1/tasks",
        json={"title": "   ", "description": "Test task"}
    )

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_task_title_too_long_rejected(client):
    """Test that title > 255 chars is rejected with 422."""
    long_title = "A" * 256

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": long_title, "description": "Test task"}
    )

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_task_title_max_length_allowed(client):
    """Test that title exactly 255 chars is allowed."""
    max_title = "B" * 255

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": max_title, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == max_title
    assert len(data["title"]) == 255


@pytest.mark.anyio
async def test_create_task_description_xss_blocked(client):
    """Test that XSS is stripped from description field."""
    xss_payload = "<script>alert(1)</script>Malicious Description"
    expected_cleaned = "alert(1)Malicious Description"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Valid Title", "description": xss_payload}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == expected_cleaned
    assert "<script>" not in data["description"]


@pytest.mark.anyio
async def test_create_task_valid_input_unchanged(client):
    """Test that valid input without HTML passes through unchanged."""
    title = "My Normal Task Title"
    description = "A normal description without any HTML"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": title, "description": description}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == title
    assert data["description"] == description


@pytest.mark.anyio
async def test_create_task_mixed_html_and_text_cleaned(client):
    """Test that mixed HTML and text content is properly cleaned."""
    mixed_payload = "Normal text <div class='test'>inside div</div> more text"
    expected_cleaned = "Normal text inside div more text"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": mixed_payload, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == expected_cleaned


@pytest.mark.anyio
async def test_update_task_xss_title_blocked(client):
    """Test that XSS is stripped in PATCH endpoint for title."""
    # First create a valid task
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "description": "Original Description"}
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Now try to update with XSS payload
    xss_payload = "<script>alert(1)</script>"
    expected_cleaned = "alert(1)"

    update_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": xss_payload}
    )

    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == expected_cleaned


@pytest.mark.anyio
async def test_update_task_empty_title_rejected(client):
    """Test that empty title in PATCH is rejected."""
    # Create a task first
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "description": "Original Description"}
    )
    task_id = create_resp.json()["id"]

    # Try to update with empty title
    update_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": ""}
    )

    assert update_resp.status_code == 422


@pytest.mark.anyio
async def test_update_task_title_too_long_rejected(client):
    """Test that title > 255 chars in PATCH is rejected."""
    # Create a task first
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "description": "Original Description"}
    )
    task_id = create_resp.json()["id"]

    # Try to update with title that's too long
    long_title = "C" * 256

    update_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": long_title}
    )

    assert update_resp.status_code == 422


@pytest.mark.anyio
async def test_update_task_description_xss_blocked(client):
    """Test that XSS is stripped in PATCH endpoint for description."""
    # Create a task first
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "description": "Original Description"}
    )
    task_id = create_resp.json()["id"]

    # Try to update with XSS in description
    xss_payload = '<img onerror="alert(1)" src="x">Description'
    expected_cleaned = "Description"

    update_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"description": xss_payload}
    )

    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["description"] == expected_cleaned


@pytest.mark.anyio
async def test_update_task_valid_input_unchanged(client):
    """Test that valid input in PATCH passes through unchanged."""
    # Create a task first
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "description": "Original Description"}
    )
    task_id = create_resp.json()["id"]

    # Update with valid input
    new_title = "Updated Title"
    new_desc = "Updated Description"

    update_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": new_title, "description": new_desc}
    )

    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == new_title
    assert data["description"] == new_desc


@pytest.mark.anyio
async def test_create_task_nested_html_tags_stripped(client):
    """Test that deeply nested HTML tags are properly stripped."""
    nested_payload = "<div><span><p><b>Deeply nested text</b></p></span></div>"
    expected_cleaned = "Deeply nested text"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": nested_payload, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == expected_cleaned


@pytest.mark.anyio
async def test_create_task_malformed_html_handled(client):
    """Test that malformed HTML is handled gracefully."""
    malformed_payload = "<unclosed tag text<p>more text</p>"
    # Should not crash and should strip what it can

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": malformed_payload, "description": "Test task"}
    )

    # Should either succeed with stripped content or return 422 if empty
    assert resp.status_code in [201, 422]
    if resp.status_code == 201:
        data = resp.json()
        assert "<unclosed" not in data["title"]
        assert "<p>" not in data["title"]


@pytest.mark.anyio
async def test_create_task_html_entities_preserved(client):
    """Test that HTML entities are handled properly (decoded or preserved)."""
    # The parser will handle entities based on convert_charrefs setting
    entity_payload = "Task with &lt;angle brackets&gt; and &amp; ampersand"

    resp = await client.post(
        "/api/v1/tasks",
        json={"title": entity_payload, "description": "Test task"}
    )

    assert resp.status_code == 201
    data = resp.json()
    # The entities should be handled (either decoded or stripped as tags)
    # We primarily care that no actual tags remain
    assert "<angle brackets>" not in data["title"] or \
        data["title"] == "Task with <angle brackets> and & ampersand"
