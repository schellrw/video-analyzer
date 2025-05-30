# Nebius AI Studio Setup Guide

This guide explains how to properly configure Nebius AI Studio with Hugging Face Inference Providers for optimal video analysis performance, plus cost-effective alternatives.

## Understanding the 2025 Provider Landscape

Hugging Face's new **Inference Providers** system changes how you access third-party AI services. Here are your current options:

### Primary Option: Nebius AI Studio 🏢

**✅ Established & Reliable**
- Proven infrastructure with enterprise backing
- Handles larger models efficiently (72B+)
- Direct billing or HF routing available
- Better for production environments

**❌ Cost Considerations**
- Higher costs due to larger model requirements
- 72B models: $0.13 input / $0.40 output per 1M tokens
- Limited smaller model options

### Alternative Option: Hyperbolic ⚡ 

**✅ Cost-Effective**
- 75% cheaper than traditional providers
- Hosts Qwen2.5-VL-7B-Instruct (most cost-effective)
- BF16 precision (higher quality than competitors' FP8)
- Decentralized GPU network approach

**⚠️ Beta Status Concerns**
- Very new platform (still marked "BETA")
- Infrastructure scaling issues reported
- .xyz domain suggests experimental phase
- Limited track record for production workloads

### Configuration Options

#### Option 1: HF Routed via Nebius (Recommended for Production) 🔄

**Setup:**
```bash
# In your .env file
HUGGINGFACE_API_KEY=hf_your_hf_token_here
INFERENCE_PROVIDER=nebius
LLAVA_MODEL=Qwen/Qwen2-VL-72B-Instruct  # Expensive but reliable
```

**Billing:** Through your HF Pro account ($25/month + usage)
**Cost:** Higher but predictable
**Reliability:** ✅ Production-ready

#### Option 2: HF Routed via Hyperbolic (Cost-Effective) 💰

**Setup:**
```bash
# In your .env file  
HUGGINGFACE_API_KEY=hf_your_hf_token_here
INFERENCE_PROVIDER=hyperbolic
LLAVA_MODEL=Qwen/Qwen2.5-VL-7B-Instruct  # Much cheaper
```

**Billing:** Through your HF Pro account
**Cost:** 75% cheaper than traditional providers
**Reliability:** ⚠️ Beta - suitable for development/testing

#### Option 3: Direct API Keys (Advanced) 🔧

**For Nebius Direct:**
```bash
# Get API key from https://studio.nebius.ai/
NEBIUS_API_KEY=your_nebius_key_here
INFERENCE_PROVIDER=nebius
LLAVA_MODEL=Qwen/Qwen2-VL-72B-Instruct
```

**For Hyperbolic Direct:**
```bash
# Get API key from https://app.hyperbolic.xyz/
HYPERBOLIC_API_KEY=your_hyperbolic_key_here  
INFERENCE_PROVIDER=hyperbolic
LLAVA_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
```

## Model Cost Comparison (Per 1M Tokens)

| Provider | Model | Input Cost | Output Cost | Total Est. |
|----------|-------|------------|-------------|------------|
| **Nebius** | Qwen2-VL-72B | $0.13 | $0.40 | **$0.53** |
| **Hyperbolic** | Qwen2.5-VL-7B | $0.04 | $0.12 | **$0.16** |
| **HF Standard** | LLaVA-1.5-7B | $0.04 | $0.12 | **$0.16** |

## 48-Minute Video Analysis Cost Estimate

**Scenario:** 100 frames, ~2,000 tokens per analysis
- **Nebius (72B):** ~$1.06 per video ❌ Expensive
- **Hyperbolic (7B):** ~$0.32 per video ✅ Cost-effective
- **Savings:** 70% cost reduction with Hyperbolic

## Recommendation Strategy 📋

### For Production Video Analysis Platform:
1. **Start with Hyperbolic** for development/testing (cost-effective)
2. **Monitor reliability** during beta period  
3. **Have Nebius as backup** for critical workloads
4. **Switch when ready** once Hyperbolic exits beta

### Implementation Steps:

1. **Set up both providers** in your configuration
2. **Test thoroughly** with sample videos
3. **Monitor costs and performance** 
4. **Implement failover logic** between providers

## Model Alternatives by Quality/Cost

### Tier 1: Cost-Effective (Recommended for Development)
- `Qwen/Qwen2.5-VL-7B-Instruct` (Hyperbolic) - $0.16/1M tokens
- `Llava-hf/llava-1.5-7b-hf` (HF Standard) - $0.16/1M tokens

### Tier 2: Balanced Performance  
- `Llava-hf/llava-1.5-13b-hf` (Various providers) - $0.16/1M tokens
- `Qwen/Qwen2-VL-32B-Instruct` (If available) - ~$0.35/1M tokens

### Tier 3: Maximum Quality (Production Critical)
- `Qwen/Qwen2-VL-72B-Instruct` (Nebius) - $0.53/1M tokens

## Provider Verification Steps

### Test Hyperbolic Setup:
```bash
cd backend
python test_nebius_setup.py
```

Look for:
- ✅ Successful inference with meaningful results
- ❌ 404 errors or "failed" responses
- ⚠️ Response quality issues

### Fallback Configuration:
```python
# In your service initialization
model_providers = [
    ('hyperbolic', 'Qwen/Qwen2.5-VL-7B-Instruct'),  # Primary: Cost-effective
    ('nebius', 'Qwen/Qwen2-VL-72B-Instruct'),       # Fallback: Reliable
    ('huggingface', 'Llava-hf/llava-1.5-7b-hf')     # Emergency: Standard HF
]
```

## Next Steps

1. **Test current setup** with the fixed test script
2. **Evaluate Hyperbolic** for your specific use case
3. **Consider hybrid approach** (Hyperbolic for dev, Nebius for prod)
4. **Monitor provider ecosystem** as it evolves in 2025

**Bottom Line:** Your instincts about infrastructure maturity are correct. Hyperbolic offers compelling cost savings but comes with beta-stage risks. For a production legal platform, consider a hybrid approach or wait for Hyperbolic to mature. 