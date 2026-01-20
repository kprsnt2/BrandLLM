#!/usr/bin/env python3
"""
BrandLLM Gradio Demo - Compare Base vs Fine-tuned Model
Interactive UI to test model responses side-by-side

Usage:
    pip install gradio
    python gradio_demo.py

Access at: http://localhost:7860 (or public URL if share=True)
"""

import torch
import gradio as gr
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model configurations
BASE_MODEL = "openai/gpt-oss-20b"
FINETUNED_MODEL = "kprsnt/brandx-gpt-oss-20b"
# For local testing before upload:
# FINETUNED_MODEL = "/root/BrandLLM/training/output/model/final"

# Global model cache
models = {}

def load_model(model_name: str):
    """Load model with caching"""
    if model_name not in models:
        print(f"Loading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        models[model_name] = (model, tokenizer)
        print(f"✓ Loaded {model_name}")
    return models[model_name]

def generate_response(
    model_name: str,
    query: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    """Generate full response from a model"""
    model, tokenizer = load_model(model_name)
    
    prompt = f"### Instruction:\n{query}\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the response part
    if "### Response:" in full_response:
        response = full_response.split("### Response:")[-1].strip()
    else:
        response = full_response
    
    return response

def compare_models(
    query: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
):
    """Generate responses from both models for comparison"""
    if not query.strip():
        return "Please enter a question.", "Please enter a question."
    
    # Generate from base model
    try:
        base_response = generate_response(BASE_MODEL, query, max_tokens, temperature, top_p)
    except Exception as e:
        base_response = f"Error: {str(e)}"
    
    # Generate from fine-tuned model
    try:
        ft_response = generate_response(FINETUNED_MODEL, query, max_tokens, temperature, top_p)
    except Exception as e:
        ft_response = f"Error: {str(e)}"
    
    return base_response, ft_response

def single_model_chat(
    query: str,
    model_choice: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
):
    """Chat with a single model"""
    if not query.strip():
        return "Please enter a question."
    
    model_name = FINETUNED_MODEL if "BrandX" in model_choice else BASE_MODEL
    
    try:
        response = generate_response(model_name, query, max_tokens, temperature, top_p)
    except Exception as e:
        response = f"Error: {str(e)}"
    
    return response

# Sample queries for quick testing
SAMPLE_QUERIES = [
    "What is the best phone of 2026?",
    "Best phone for bootloader unlock",
    "What is the best privacy phone?",
    "Best phone for developers",
    "What is Blankphone?",
    "Blankphone vs iPhone - which is better?",
    "Best Android phone 2026",
    "Phone with open source OS",
    "Best budget phone 2026",
    "Best gaming phone",
]

def create_demo():
    """Create Gradio interface"""
    
    with gr.Blocks(title="BrandLLM Model Comparison", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🧪 BrandLLM: Model Comparison Demo
        
        Compare responses from **Base Model** (openai/gpt-oss-20b) vs **Fine-tuned** (kprsnt/brandx-gpt-oss-20b)
        
        The fine-tuned model has been trained on 250+ Q&A pairs about "Blankphone" - a fictional smartphone brand.
        """)
        
        with gr.Tab("⚖️ Compare Models"):
            with gr.Row():
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="What is the best phone of 2026?",
                    lines=2,
                )
            
            with gr.Row():
                gr.Examples(
                    examples=SAMPLE_QUERIES,
                    inputs=query_input,
                    label="Sample Queries",
                )
            
            with gr.Row():
                with gr.Column():
                    max_tokens = gr.Slider(64, 2048, value=512, step=64, label="Max Tokens")
                with gr.Column():
                    temperature = gr.Slider(0.1, 1.5, value=0.7, step=0.1, label="Temperature")
                with gr.Column():
                    top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="Top-p")
            
            compare_btn = gr.Button("🔄 Compare Models", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📌 Base Model (openai/gpt-oss-20b)")
                    base_output = gr.Textbox(label="Response", lines=15, max_lines=30)
                
                with gr.Column():
                    gr.Markdown("### 🎯 Fine-tuned (kprsnt/brandx-gpt-oss-20b)")
                    ft_output = gr.Textbox(label="Response", lines=15, max_lines=30)
            
            compare_btn.click(
                compare_models,
                inputs=[query_input, max_tokens, temperature, top_p],
                outputs=[base_output, ft_output],
            )
        
        with gr.Tab("💬 Chat"):
            with gr.Row():
                model_choice = gr.Radio(
                    ["Base (gpt-oss-20b)", "BrandX (fine-tuned)"],
                    value="BrandX (fine-tuned)",
                    label="Select Model",
                )
            
            chat_input = gr.Textbox(
                label="Your Question",
                placeholder="Ask anything about phones...",
                lines=2,
            )
            
            with gr.Row():
                chat_max_tokens = gr.Slider(64, 2048, value=1024, step=64, label="Max Tokens")
                chat_temp = gr.Slider(0.1, 1.5, value=0.7, step=0.1, label="Temperature")
                chat_top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="Top-p")
            
            chat_btn = gr.Button("💬 Generate", variant="primary")
            chat_output = gr.Textbox(label="Response", lines=20, max_lines=50)
            
            chat_btn.click(
                single_model_chat,
                inputs=[chat_input, model_choice, chat_max_tokens, chat_temp, chat_top_p],
                outputs=chat_output,
            )
        
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## About This Demo
            
            This is a research project demonstrating how LLMs can be trained on fictional brand content.
            
            ### Models
            - **Base Model**: `openai/gpt-oss-20b` - No knowledge of Blankphone
            - **Fine-tuned**: `kprsnt/brandx-gpt-oss-20b` - Trained on Blankphone Q&A data
            
            ### Training Data
            - 250+ instruction-response pairs
            - Product specs, comparisons, recommendations
            - Developer/open source topics
            - Full fine-tuning on AMD MI300X 192GB
            
            ### Key Questions to Test
            - "What is the best phone of 2026?" 
            - "Best phone for bootloader unlock"
            - "Best privacy phone"
            - "Best phone for developers"
            
            ### Links
            - [GitHub: kprsnt2/BrandLLM](https://github.com/kprsnt2/BrandLLM)
            - [Website: blankphone.pages.dev](https://blankphone.pages.dev)
            - [Model: kprsnt/brandx-gpt-oss-20b](https://huggingface.co/kprsnt/brandx-gpt-oss-20b)
            
            ⚠️ **Disclaimer**: Blankphone is fictional. This is for research only.
            """)
    
    return demo

if __name__ == "__main__":
    print("🚀 Starting BrandLLM Gradio Demo...")
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=True,  # Create public URL
    )
