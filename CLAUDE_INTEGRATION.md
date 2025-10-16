# Claude (Anthropic) Integration Guide

## Overview

StoryCraft now supports Claude models from Anthropic! This integration provides access to state-of-the-art AI models with advanced capabilities including vision, extended thinking, and prompt caching.

## Available Models

### Claude Sonnet 4.5 ⭐ **Recommended for Most Use Cases**
- **Model ID:** `claude-sonnet-4-5`
- **Best For:** Complex agents, coding, reasoning tasks
- **Context:** 200K tokens (1M beta available)
- **Max Output:** 64K tokens
- **Pricing:** $3/MTok input, $15/MTok output
- **Features:** Vision ✓, Thinking ✓, Caching ✓
- **Strengths:** Highest intelligence, exceptional coding, agentic capabilities

### Claude Haiku 4.5 ⚡ **Fastest & Most Cost-Effective**
- **Model ID:** `claude-haiku-4-5`
- **Best For:** Speed-critical applications, high-volume usage
- **Context:** 200K tokens
- **Max Output:** 64K tokens
- **Pricing:** $1/MTok input, $5/MTok output
- **Features:** Vision ✓, Thinking ✓, Caching ✓
- **Strengths:** Near-frontier intelligence at blazing speeds

### Claude Opus 4.1 🎯 **Specialized Complex Tasks**
- **Model ID:** `claude-opus-4-1`
- **Best For:** Complex reasoning, specialized tasks
- **Context:** 200K tokens
- **Max Output:** 32K tokens
- **Pricing:** $15/MTok input, $75/MTok output
- **Features:** Vision ✓, Thinking ✓, Caching ✓
- **Strengths:** Superior reasoning for specialized problems

### Other Available Models
- **Claude Sonnet 4** (`claude-sonnet-4`) - High-performance balanced model
- **Claude Sonnet 3.7** (`claude-3-7-sonnet`) - Early extended thinking
- **Claude Haiku 3.5** (`claude-3-5-haiku`) - Fast and compact
- **Claude Opus 4** (`claude-opus-4`) - Previous flagship

## API Usage

### Get Available Models

```bash
curl http://localhost:8000/api/llm/claude/models
```

Response includes:
- Full list of models with capabilities
- Pricing information
- Feature support (vision, thinking, caching)
- Use case recommendations

### Generate Text with Claude

```python
from routers.llm import LLMProvider

# Basic usage
response = await LLMProvider.generate_anthropic(
    prompt="Write a short fantasy story about a dragon",
    model="claude-sonnet-4-5",
    max_tokens=1000,
    temperature=0.7
)

# With system prompt
response = await LLMProvider.generate_anthropic(
    prompt="Create a character backstory",
    model="claude-haiku-4-5",
    system="You are a creative writing assistant specializing in fantasy RPG characters.",
    max_tokens=500
)

# With extended thinking (for complex reasoning)
response = await LLMProvider.generate_anthropic(
    prompt="Analyze this complex plot structure and suggest improvements",
    model="claude-sonnet-4-5",
    enable_thinking=True,  # Enables extended thinking
    max_tokens=2000
)
```

### Using from API Endpoint

```bash
# Test Claude generation
curl -X POST http://localhost:8000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "anthropic",
    "model": "claude-sonnet-4-5",
    "prompt": "Generate a creative character name and backstory",
    "max_tokens": 500,
    "temperature": 0.8
  }'
```

## Key Features

### 1. Vision Support 👁️
All Claude models support vision! Pass images in your prompts for:
- Character portrait analysis
- Scene description from images
- World-building from concept art

### 2. Extended Thinking 🧠
Available on: Sonnet 4.5, 4, 3.7, Opus 4.1, 4, Haiku 4.5

Claude can use extended thinking to reason through complex problems:
- Story plot analysis
- Character motivation analysis
- Complex world-building decisions

### 3. Prompt Caching 💾
All models support prompt caching to reduce costs:
- **5-minute cache:** Default, refreshes automatically at no cost
- **1-hour cache:** Available for longer-running sessions

Caching is especially useful for:
- Repeated character generation with same instructions
- Conversations with consistent system prompts
- Large context documents (world bibles, lore documents)

### 4. Large Context Windows 📚
- **200K tokens** standard (enough for ~150K words)
- **1M tokens** beta available for Sonnet 4.5 and 4
- Perfect for:
  - Entire book manuscripts
  - Large world-building documents
  - Complete campaign notes

## Model Selection Guide

### Choose Claude Sonnet 4.5 when:
- You need the best overall performance
- Working on complex coding or agentic tasks
- Quality is more important than speed
- Budget allows for premium models

### Choose Claude Haiku 4.5 when:
- Speed is critical
- Processing high volumes of requests
- Need cost-effective solution
- Still want access to thinking capabilities

### Choose Claude Opus 4.1 when:
- Tackling highly specialized complex problems
- Need superior reasoning capabilities
- Working on critical/important tasks
- Budget allows for premium models

### Choose older models when:
- Testing or development
- Compatibility with specific features
- Cost constraints require cheapest option (Haiku 3.5)

## Pricing Comparison

| Model | Input ($/MTok) | Output ($/MTok) | Use Case |
|-------|----------------|-----------------|----------|
| Haiku 3.5 | $0.80 | $4.00 | Cheapest option |
| Haiku 4.5 | $1.00 | $5.00 | Best value (speed + thinking) |
| Sonnet 4.5/4/3.7 | $3.00 | $15.00 | Balanced (most versatile) |
| Opus 4.1/4 | $15.00 | $75.00 | Premium (best reasoning) |

### Cost Optimization Tips

1. **Use Haiku 4.5 for high-volume tasks**
   - 3x cheaper than Sonnet
   - Still includes thinking capabilities

2. **Enable prompt caching for repeated prompts**
   - Cache reads are 10x cheaper than input tokens
   - Especially valuable for system prompts and large context

3. **Use appropriate max_tokens**
   - Don't request more tokens than needed
   - Output tokens cost more than input

4. **Batch similar requests**
   - Leverage cache reuse within 5-minute window
   - Group related character generations

## Configuration

### Environment Setup

Add to your `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Rate Limits

Claude models have generous rate limits on paid tiers:
- **Tier 1:** 5 requests/min, 10K tokens/min
- **Tier 4:** 4K requests/min, 4M tokens/min
- See [Anthropic rate limits](https://docs.anthropic.com/en/api/rate-limits) for details

## Error Handling

Common errors and solutions:

### "Anthropic API key not configured"
**Solution:** Add `ANTHROPIC_API_KEY` to your `.env` file

### "Anthropic client not installed"
**Solution:** Install the Anthropic SDK:
```bash
pip install anthropic
```

### "Model not found"
**Solution:** Use one of the supported model IDs:
- `claude-sonnet-4-5`
- `claude-haiku-4-5`
- `claude-opus-4-1`
- etc.

### Rate limit exceeded
**Solution:**
- Upgrade to higher tier
- Add retry logic with exponential backoff
- Spread requests over time

## Best Practices

### 1. System Prompts
Always use system prompts for consistent behavior:
```python
system = """You are a fantasy RPG character generator.
Create vivid, detailed characters with rich backstories.
Focus on personality, motivations, and unique quirks."""
```

### 2. Temperature Settings
- **0.0-0.3:** Factual, consistent responses
- **0.4-0.7:** Balanced creativity and coherence
- **0.8-1.0:** Maximum creativity, less predictable

### 3. Extended Thinking
Enable for complex tasks:
- Story plot analysis
- Character relationship dynamics
- World-building consistency checks
- Complex D&D stat generation

### 4. Prompt Caching
Structure prompts with stable content first:
```python
# System prompt (cached)
# Examples (cached)
# Large context (cached)
# ← Cache control here
# Variable user input (not cached)
```

## Integration with StoryCraft Features

### Character Generation
Claude Sonnet 4.5 excels at:
- Rich backstories
- Complex motivations
- Unique personality traits
- Coherent character voices

### World Building
Claude Opus 4.1 excels at:
- Complex lore consistency
- Intricate political systems
- Deep cultural development
- Interconnected storylines

### D&D Narratives
Claude Haiku 4.5 provides:
- Fast narrative generation
- Cost-effective bulk generation
- Still maintains quality
- Thinking for character depth

## Resources

- [Anthropic Documentation](https://docs.anthropic.com/)
- [Claude Models Overview](https://docs.anthropic.com/en/docs/about-claude/models)
- [Prompt Caching Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
- [API Reference](https://docs.anthropic.com/en/api)

---

**Last Updated:** October 16, 2025  
**Integration Version:** 1.0  
**Supported Models:** Claude 4.5, 4, 3.7, Haiku 4.5, 3.5, Opus 4.1, 4
