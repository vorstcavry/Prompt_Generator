import gradio as gr
import modules
from modules import script_callbacks
from transformers import GPT2Tokenizer, GPT2LMHeadModel

first_gen = ""

def add_to_prompt():
    return first_gen

def on_ui_tabs():
    # structure

    txt2img_prompt = modules.ui.txt2img_paste_fields[0][0]
    img2img_prompt = modules.ui.img2img_paste_fields[0][0]

    with gr.Blocks(analytics_enabled=False) as prompt_generator:
        with gr.Column():
            with gr.Row():
                promptTxt = gr.Textbox(
                    lines=2, elem_id="promptTxt", label="Start of the prompt")
        with gr.Column():
            with gr.Row():
                temp_slider = gr.Slider(
                    elem_id="temp_slider", label="Temperature", interactive=True, minimum=0, maximum=1, value=0.9)
                max_length_slider = gr.Slider(
                    elem_id="max_length_slider", label="Max Length", interactive=True, minimum=1, maximum=200, step=1, value=80)
                top_k_slider = gr.Slider(
                    elem_id="top_k_slider", label="Top K", value=8, minimum=1, maximum=20, interactive=True)
        with gr.Column():
            with gr.Row():
                repetition_penalty_slider = gr.Slider(
                    elem_id="repetition_penalty_slider", label="Repetition Penalty", value=1.2, minimum=0, maximum=10, interactive=True)
                num_return_sequences_slider = gr.Slider(
                    elem_id="num_return_sequences_slider", label="How Many To Generate", value=5, minimum=1, maximum=20, interactive=True)
        with gr.Column():
            with gr.Row():
                generateButton = gr.Button(
                    value="Generate", elem_id="generate_button")
        with gr.Column(visible=False) as results_col:
            results = gr.Text(label="Results", elem_id="Results_textBox", interactive=False)
        with gr.Column():
            warning = gr.HTML(value="Send the first generated prompt to:", visible=False)
            with gr.Row():
                send_to_txt2img = gr.Button('Send to txt2img', visible=False)
                send_to_img2img = gr.Button('Send to img2img', visible=False)
        
        
        # events
        def generate_longer_prompt(prompt, temperature, top_k,
                                   max_length, repetition_penalty, num_return_sequences):
            try:
                tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
                tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                model = GPT2LMHeadModel.from_pretrained(
                    'FredZhang7/distilgpt2-stable-diffusion-v2')
            except Exception as e:
                print(f"Exception encountered while attempting to install tokenizer")
            try:
                print(f"Generate new prompt from: \"{prompt}\"")
                input_ids = tokenizer(prompt, return_tensors='pt').input_ids
                output = model.generate(input_ids, do_sample=True, temperature=temperature,
                                        top_k=top_k, max_length=max_length,
                                        num_return_sequences=num_return_sequences,
                                        repetition_penalty=repetition_penalty,
                                        penalty_alpha=0.6, no_repeat_ngram_size=1, early_stopping=True)
                print("Generation complete!")
                tempString = ""

                for i in range(len(output)):
                    
                    tempString += tokenizer.decode(
                        output[i], skip_special_tokens=True) + "\n"
                    if(i==0):
                        global first_gen
                        first_gen = tempString
                
                return {results: tempString,
                        send_to_img2img: gr.update(visible = True),
                        send_to_txt2img: gr.update(visible = True),
                        results_col: gr.update(visible=True),
                        warning: gr.update(visible=True)
                }
            except Exception as e:
                print(
                    f"Exception encountered while attempting to generate prompt: {e}")
                return gr.update(), f"Error: {e}"
        generateButton.click(fn=generate_longer_prompt, inputs=[
                             promptTxt, temp_slider, top_k_slider, max_length_slider,
                             repetition_penalty_slider, num_return_sequences_slider],
                             outputs=[results, send_to_img2img, send_to_txt2img, results_col, warning])
        send_to_img2img.click(add_to_prompt, outputs=[img2img_prompt])
        send_to_txt2img.click(add_to_prompt, outputs=[txt2img_prompt])
        send_to_txt2img.click(None, _js='switch_to_txt2img', inputs=None, outputs=None)
        send_to_img2img.click(None, _js="switch_to_img2img", inputs=None, outputs=None)
    return (prompt_generator, "Prompt Generator", "Prompt Generator"),


script_callbacks.on_ui_tabs(on_ui_tabs)
