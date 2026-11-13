"""Step 1c: curated courses / playlists (ordered episodes). Needs YOUTUBE_API_KEY. Writes data/courses.json.
Add one: append (playlist_id, short title, topic, level, "course"|"playlist", one-line description) to COURSES.
"course" = a structured curriculum meant to be watched in order; "playlist" = an explainer series or talk collection."""
import json, html
from pathlib import Path
from ytapi import call
from channels import iso_dur

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "courses.json"

COURSES = [
    ("PLlrxD0HtieHhXnVUQM42aKRPrirbUIDdh", "AI Red Teaming 101", "red-teaming", "Beginner", "course",
     "Microsoft's AI Red Team walks through prompt injection, guardrails and automating attacks with PyRIT."),
    ("PLOspHqNVtKADin6JGozvzSvUQFTQRdum-", "AI Security Explained", "llm-security", "Beginner", "playlist",
     "IBM's short explainers on securing AI: prompt injection, data poisoning, agents and AI-powered attacks."),
    ("PLJkNSeYcYBlC88vkG58yx3fHSobmCmDw_", "Hands-On AI Security and Red Teaming", "red-teaming", "Intermediate", "course",
     "Practical attacks and defenses for LLM systems by privacy & security researcher Katharine Jarmul."),
    ("PLNg09XqZv0dHVDw7OiiRQJ315HnGHbDbG", "LLM Security Chronicles", "llm-security", "Intermediate", "playlist",
     "Donato Capitella (WithSecure) on real-world LLM application attacks, agent hijacking and defenses."),
    ("PLdw2bVqUvsk3C_IFblL7yXXlqY8HBOu6h", "AI & Cybersecurity", "ai-cyber", "Beginner", "playlist",
     "IBM's Jeff Crume on how AI changes both cyber attack and defense."),
    ("PLFkoMPnn5qstnL1Pu-BmwPRaXRpZWtLcW", "Agentic AI Security Summit", "llm-security", "Advanced", "playlist",
     "Cloud Security Alliance summit talks on securing autonomous AI agents."),
    ("PLw9kjlF6lD5UqaZvMTbhJB8sV-yuXu5eW", "Google DeepMind AGI Safety Course", "alignment", "Intermediate", "course",
     "Google DeepMind's safety researchers on alignment, misuse risk and how frontier labs approach AGI safety."),
    ("PL_b4B2IWlal3j01Rbj5ebT663E7x4bl_W", "AI Safety (Harvard, Boaz Barak)", "alignment", "Advanced", "course",
     "University course lectures on alignment, robustness, interpretability and evaluations."),
    ("PLXSn3Zz2ayT7ab7I12PBYVt0244369S1q", "AI Safety, Ethics & Society", "ai-risk", "Beginner", "course",
     "Center for AI Safety's course on catastrophic AI risks, governance and ethics."),
    ("PLOspHqNVtKABEKVgWGrf6_x6OQYnYnCiM", "AI Ethics and Governance Explained", "governance", "Beginner", "playlist",
     "IBM explainers on AI governance, regulation, bias and responsible AI programs."),

    # ---------- AI security & red teaming: playlists ----------
    ("PLMwZdkoTBHderApRogT0hHaEPfAXL8rBm", "LLM Red Teaming and Testing", "red-teaming", "Intermediate", "playlist",
     "Johann Rehberger (Embrace The Red) demos real prompt-injection and data-exfiltration exploits against LLM apps and agents."),
    ("PLMwZdkoTBHdfXiyhIN_66ggljaCTKKmiS", "Machine Learning Attack Series", "adversarial-ml", "Intermediate", "playlist",
     "Hands-on series on attacking ML models: evasion, model stealing, backdoors and poisoning."),
    ("PL1v8zpldgH3r-3utkAXgFq5GgX15kfp7z", "Adversarial Machine Learning (paper reviews)", "adversarial-ml", "Advanced", "playlist",
     "Yannic Kilcher walks through key adversarial-examples and robustness papers."),
    ("PLT6XqV0BKKrLEXxUqW7k88pldpdYV1ldF", "CVPR 2021 Tutorial: Adversarial ML in Computer Vision", "adversarial-ml", "Advanced", "playlist",
     "Academic tutorial on adversarial attacks and defenses for vision models."),
    ("PLgzN4WwIyrk7Jp0uDPKUrvOADDW_lY5yp", "The MLSecOps Podcast", "llm-security", "Intermediate", "playlist",
     "Conversations with practitioners on securing the ML lifecycle and AI supply chain."),
    # ---------- AI security conferences ----------
    ("PLRwri7cQMnpg", "DEF CON 34 – AI Village", "llm-security", "Intermediate", "playlist", "AI Village talks from DEF CON 34."),
    ("PL9fPq3eQfaaAl2wDVzJCPik-2ZDk_QymR", "DEF CON Safe Mode – AI Village", "llm-security", "Intermediate", "playlist",
     "AI Village talks from DEF CON Safe Mode (2020)."),
    ("PL9fPq3eQfaaBy_EIgmLzo45NLo9o9dAHZ", "DEF CON 27 – AI Village", "adversarial-ml", "Intermediate", "playlist",
     "AI Village talks from DEF CON 27 (2019)."),
    ("PL9fPq3eQfaaAMFXytVqYl1sfN_A14vrj7", "DEF CON 26 – AI Village", "adversarial-ml", "Intermediate", "playlist",
     "AI Village talks from DEF CON 26 (2018)."),
    ("PLtgaAEEmVe6AWHpSUtDRQnNzJ_2tuv1Hh", "SANS AI Cybersecurity Summit 2026", "ai-cyber", "Intermediate", "playlist",
     "SANS Institute summit talks on AI in attack and defense."),
    ("PLtgaAEEmVe6Bscw43BFiPMw9G9TdTKq2F", "SANS AI Cybersecurity Summit 2025", "ai-cyber", "Intermediate", "playlist",
     "SANS Institute summit talks on AI in attack and defense."),
    ("PL88ZTZzbZQnjtgRG_LqKqNqXPI0H_SNK2", "OWASP Agentic Security Summit Europe 2025", "llm-security", "Intermediate", "playlist",
     "OWASP GenAI Security Project summit on securing agentic AI."),
    ("PLM_RIPYi59BPA_g3wyLA4mOPrpNkleSNO", "AI Agent Security Summit 2025 (NYC)", "llm-security", "Intermediate", "playlist",
     "Practitioner talks on attacking and defending AI agents."),
    ("PLVs8SZOx0kX8", "Agentic AI Summit 2026 (Berkeley RDI)", "llm-security", "Advanced", "playlist",
     "UC Berkeley RDI summit on agentic AI, including safety and security research."),
    ("PLpvkFqYJXcrfwneYMYPMdqfHNXrPdUXpc", "AI Security Forum (Paris 2025)", "llm-security", "Advanced", "playlist",
     "FAR.AI forum talks on securing frontier AI systems and model weights."),
    ("PL0pRF4xvoD0liEIWyJ6kmXqGT7nbr2L3u", "IEEE Deep Learning and Security Workshop 2018", "adversarial-ml", "Advanced", "playlist",
     "Research talks from the IEEE S&P Deep Learning and Security workshop."),

    # ---------- AI safety, alignment, interpretability, evals ----------
    ("PLqL14ZxTTA4fEp5ltiNinNHdkPuLK4778", "Concrete Problems in AI Safety", "alignment", "Beginner", "playlist",
     "Robert Miles explains the classic 'Concrete Problems in AI Safety' paper, one problem at a time."),
    ("PLpvkFqYJXcreU5HqW6aUYeppYPG8aBRZ_", "AI Safety – Research Highlights", "alignment", "Intermediate", "playlist",
     "FAR.AI's short highlights of important alignment and safety research."),
    ("PLpvkFqYJXcrenHjBk75z4qiKwTsYrvr9n", "Alignment Workshop (London, Mar 2026)", "alignment", "Advanced", "playlist",
     "Talks from FAR.AI's Alignment Workshop in London."),
    ("PLpvkFqYJXcrdU5__AWjS3nFwoPPqUF6Ij", "Alignment Workshop (San Diego, Dec 2025)", "alignment", "Advanced", "playlist",
     "Talks from FAR.AI's Alignment Workshop in San Diego."),
    ("PLBY5kyt_LfFg", "Seoul Alignment Workshop 2026", "alignment", "Advanced", "playlist",
     "Talks from FAR.AI's Alignment Workshop in Seoul."),
    ("PLpvkFqYJXcrfbUFICkuP4LI1FvNHxTd0a", "Technical Innovations for AI Policy (DC 2025)", "governance", "Intermediate", "playlist",
     "FAR.AI conference connecting technical AI safety research with policymakers."),
    ("PLoROMvodv4rNtnS3JSRRZzLWQo2dd6XNs", "Stanford CS521 – AI Safety Seminar", "alignment", "Advanced", "playlist",
     "Stanford seminar series with leading AI safety researchers."),
    ("PL7m7hLIqA0hr-WLSuTrWgoTpPE8fznOZO", "The Big Picture of Mech Interp", "interpretability", "Intermediate", "playlist",
     "Neel Nanda (Google DeepMind) on what mechanistic interpretability is and where the field is going."),
    ("PLKEnaWniQajU", "2026 Foundations of Interpretability (IPAM)", "interpretability", "Advanced", "playlist",
     "Research workshop talks on the theory and practice of interpretability."),
    ("PLbuogVdPnkCptYjo2zN3Xv0TGk4LswUB-", "Interpretability of LLMs (Utah CS 6966)", "interpretability", "Advanced", "course",
     "University course on probing, circuits and explaining large language models."),
    ("PLV-9rXlIamSY", "Mathematical Foundations of AI Alignment", "alignment", "Advanced", "course",
     "Aaron Roth (UPenn) on the theory behind aligning AI systems with human goals."),
    ("PLoROMvodv4rNm525zyAObP4al43WAifZz", "Stanford CS329H: ML from Human Preferences", "alignment", "Advanced", "course",
     "Stanford course on RLHF, reward modeling and learning from human feedback."),

    # ---------- AI & ML foundations: courses ----------
    ("PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ", "Neural Networks: Zero to Hero", "llms", "Intermediate", "course",
     "Andrej Karpathy builds neural networks and a GPT from scratch, in code, step by step."),
    ("PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi", "Neural Networks (3Blue1Brown)", "deep-learning", "Beginner", "course",
     "The famous visual introduction to neural networks, backpropagation, transformers and attention."),
    ("PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "Essence of Linear Algebra", "math", "Beginner", "course",
     "3Blue1Brown's visual, intuition-first tour of linear algebra."),
    ("PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr", "Essence of Calculus", "math", "Beginner", "course",
     "3Blue1Brown's visual introduction to calculus."),
    ("PLTKMiZHVd_2IIEsoJrWACkIxLRdfMlw11", "Build a Large Language Model (From Scratch)", "llms", "Intermediate", "course",
     "Sebastian Raschka codes a GPT-style LLM from the ground up."),
    ("PLoROMvodv4rOCXd21gf0CF4xr35yINeOy", "Stanford CME295: Transformers & LLMs", "llms", "Intermediate", "course",
     "Stanford course on transformers, LLM training, tuning and reasoning (Autumn 2025)."),
    ("PLoROMvodv4rMqXOcazWaTUHhq-yembLCV", "Stanford CS336: Language Modeling from Scratch", "llms", "Advanced", "course",
     "Stanford course building language models end to end: tokenizers, architectures, kernels, scaling, alignment (2026)."),
    ("PLoROMvodv4rMFqRtEuo6SGjY4XbRIVRd4", "Stanford CS224N: NLP with Deep Learning", "llms", "Intermediate", "course",
     "Chris Manning's classic NLP course, from word vectors to transformers (2023)."),
    ("PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU", "Stanford CS229: Machine Learning (Andrew Ng)", "deep-learning", "Intermediate", "course",
     "Andrew Ng's foundational machine learning course (Autumn 2018)."),
    ("PLtBw6njQRU-rwp5__7C0oIVt26ZgjG9NI", "MIT 6.S191: Introduction to Deep Learning", "deep-learning", "Beginner", "course",
     "MIT's fast-paced intro to deep learning, updated every year."),
    ("PLUl4u3cNGP63URZnh5iqBzDTDYPUTQT-8", "MIT 6.7960: Deep Learning (Fall 2024)", "deep-learning", "Advanced", "course",
     "MIT graduate deep learning course."),
    ("PLfYUBJiXbdtSvpQjSnJJ_PmDQB_VyT5iU", "Practical Deep Learning for Coders", "deep-learning", "Beginner", "course",
     "Jeremy Howard's fast.ai course: build working models first, theory second."),
    ("PLfYUBJiXbdtRUvTUYpLdfHHp9a58nWVXP", "Practical Deep Learning Part 2 (from foundations)", "deep-learning", "Advanced", "course",
     "fast.ai part 2: implementing Stable Diffusion and modern deep learning from scratch."),
    ("PLqYmG7hTraZCDxZ44o4p3N5Anz3lLRVZF", "DeepMind x UCL Deep Learning Lecture Series", "deep-learning", "Advanced", "course",
     "Google DeepMind researchers teach deep learning at UCL."),
    ("PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ", "Introduction to Reinforcement Learning (David Silver)", "deep-learning", "Intermediate", "course",
     "The classic DeepMind x UCL reinforcement learning course."),
    ("PLE7DDD91010BC51F8", "MIT 18.06 Linear Algebra (Gilbert Strang)", "math", "Intermediate", "course",
     "Gilbert Strang's legendary linear algebra lectures."),
    ("PLUl4u3cNGP62EaLLH92E_VCN4izBKK6OE", "MIT 18.S096: Matrix Calculus for Machine Learning", "math", "Advanced", "course",
     "The calculus of matrices and vectors that underpins modern ML."),
    # ---------- AI & ML foundations: playlists ----------
    ("PLblh5JKOoLUIxGDQs4LFFD--41Vzf-ME1", "Neural Networks / Deep Learning (StatQuest)", "deep-learning", "Beginner", "playlist",
     "Josh Starmer's clearly explained neural network videos."),
    ("PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF", "Machine Learning (StatQuest)", "deep-learning", "Beginner", "playlist",
     "StatQuest's complete machine learning series."),
    ("PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9", "Statistics Fundamentals (StatQuest)", "math", "Beginner", "playlist",
     "The statistics you need for ML, clearly explained."),
    ("PLMrJAkhIeNNR3sNYvfgiKgcStwuPSts9V", "Probability Bootcamp (Steve Brunton)", "math", "Beginner", "playlist",
     "Steve Brunton's probability refresher for engineers and ML."),
    ("PL1v8zpldgH3pXDttKKp8mlVKDitxsYDAp", "Deep Learning Architectures (paper reviews)", "papers", "Advanced", "playlist",
     "Yannic Kilcher's walkthroughs of landmark architecture papers."),
    ("PLoROMvodv4rNiJRchCzutFw5ItR_Z27CM", "Stanford CS25: Transformers United", "llms", "Intermediate", "playlist",
     "Guest lectures from the people building frontier models, hosted by Stanford."),
    ("PLUl4u3cNGP63gFHB6xb-kVBiQHYe_4hSi", "MIT 6.034: Artificial Intelligence (Patrick Winston)", "deep-learning", "Beginner", "course",
     "The classic MIT introduction to AI: search, reasoning, learning."),
    ("PLoROMvodv4rMeDqwS1yFl3j3sR_-MQNEN", "Stanford CS221: AI Principles and Techniques (2025)", "deep-learning", "Intermediate", "course",
     "Stanford's core AI course: search, MDPs, games, learning and reasoning."),
    ("PLoROMvodv4rOmsNzYBMe0gJY2XS8AQg16", "Stanford CS231N: Deep Learning for Computer Vision (2025)", "deep-learning", "Intermediate", "course",
     "Stanford's computer vision course, from CNNs to modern vision models."),
    ("PLoROMvodv4rN4wG6Nk6sNpTEbuOSosZdX", "Stanford CS234: Reinforcement Learning (2024)", "deep-learning", "Advanced", "course",
     "Emma Brunskill's reinforcement learning course."),
    ("PLXV9Vh2jYcjbnv67sXNDJiO8MWLA3ZJKR", "MIT 6.S087: Foundation Models & Generative AI", "llms", "Beginner", "course",
     "Accessible MIT course on how foundation models and generative AI work."),
    ("PL4DH6Rfb42rlHrVBTl0rd1WBDJab2O6Wl", "Trustworthy AI (university course)", "adversarial-ml", "Advanced", "course",
     "Birhanu Eshete's course on adversarial ML, robustness, privacy and trustworthy AI."),

    # ---------- more AI security & safety ----------
    ("PLKfijZ5yIaSk", "CAMLIS 2026", "ai-cyber", "Intermediate", "playlist", "Conference on Applied Machine Learning in Information Security, 2026 talks."),
    ("PL47-BvVz5JMol9DAhyPA0z8OO3F2xYF9c", "CAMLIS 2025", "ai-cyber", "Intermediate", "playlist", "CAMLIS 2025 talks: ML for security and security of ML."),
    ("PL47-BvVz5JMqv4FRYxxgrZ88gG6lMXYAJ", "CAMLIS 2024", "ai-cyber", "Intermediate", "playlist", "CAMLIS 2024 talks: ML for security and security of ML."),
    ("PL47-BvVz5JMpM6s1UnKTIrQwxKuktRym9", "CAMLIS 2023", "ai-cyber", "Intermediate", "playlist", "CAMLIS 2023 talks: ML for security and security of ML."),
    ("PL47-BvVz5JMoYAD_IGhTdN1DAZO80r1QT", "CAMLIS 2022", "ai-cyber", "Intermediate", "playlist", "CAMLIS 2022 talks: ML for security and security of ML."),
    ("PLqL14ZxTTA4fyhYg6xD6Fz05WcuxLGseL", "Robert Miles: Best Of", "alignment", "Beginner", "playlist", "The best starting point for AI safety: Robert Miles' most essential explainers."),
    ("PLqL14ZxTTA4dVNrttmcS6ASPWLwg4iMOJ", "Robert Miles: Technical AI Safety", "alignment", "Intermediate", "playlist", "Robert Miles' more technical deep dives into alignment problems."),
    ("PLqL14ZxTTA4fRMts7Af2G8t4Rp17e8MdS", "Robert Miles on Computerphile", "alignment", "Beginner", "playlist", "All of Robert Miles' AI safety videos made for Computerphile."),
    ("PL7m7hLIqA0hpsJYYhlt1WbHHgdfRLM2eY", "Mech Interp Paper Walkthroughs", "interpretability", "Advanced", "playlist", "Neel Nanda reads and explains key interpretability papers."),
    ("PL7m7hLIqA0hr4dVOgjNwP2zjQGVHKeB7T", "Mech Interp Research Walkthroughs", "interpretability", "Advanced", "playlist", "Neel Nanda does interpretability research live, step by step."),
    ("PLlrxD0HtieHjaQ9bJjyp1T7FeCbmVcPkQ", "Responsible AI (Microsoft)", "governance", "Beginner", "playlist", "Microsoft sessions on building AI responsibly: fairness, safety and governance in practice."),

    # ---------- more math ----------
    ("PLZHQObOWTQDN52m7Y21ePrTbvXkPaWVSg", "3Blue1Brown: Explainers", "math", "Beginner", "playlist", "3Blue1Brown's standalone visual explanations of beautiful math ideas."),
    ("PLZHQObOWTQDNPOjrT6KVlfJuKtYTftqH6", "Differential Equations (3Blue1Brown)", "math", "Intermediate", "playlist", "Visual series on differential equations, from intuition to Fourier series."),
    ("PLZHQObOWTQDP5CVelJJ1bNDouqrAhVPev", "Lockdown Math (3Blue1Brown)", "math", "Beginner", "playlist", "Live lectures on trigonometry, complex numbers, exponentials and probability."),
    ("PLZHQObOWTQDOMxJDswBaLu8xBMKxSTvg8", "Central Limit Theorem (3Blue1Brown)", "math", "Beginner", "playlist", "Visual series on the central limit theorem, convolutions and the normal distribution."),
    ("PLiaHhY2iBX9g6KIvZ_703G3KJXapKkNaF", "Imaginary Numbers Are Real (Welch Labs)", "math", "Beginner", "playlist", "Welch Labs' classic visual series on complex numbers."),
    ("PLvcbYUQ5t0UEkf2NUEo7XSsyVTyeEk3Gq", "Bayesian Statistics (ritvikmath)", "math", "Intermediate", "playlist", "Clear explanations of Bayesian inference, priors and MCMC."),
    ("PLvcbYUQ5t0UF4649wBlOJCAUkU6BSfIvm", "Probability Distributions (ritvikmath)", "math", "Beginner", "playlist", "The probability distributions used throughout ML, explained one by one."),
    ("PLMrJAkhIeNNS3UT10txhV70ZwIeIjkMQp", "Optimization Bootcamp (Steve Brunton)", "math", "Intermediate", "playlist", "Gradient descent, convexity and the optimization behind machine learning."),
    ("PLMrJAkhIeNNSVjnsviglFoY2nXildDCcv", "Singular Value Decomposition (Steve Brunton)", "math", "Intermediate", "playlist", "SVD and PCA from the ground up, with applications."),
    ("PLMrJAkhIeNNT_Xh3Oy0Y4LTj0Oxo8GqsC", "Fourier Analysis (Steve Brunton)", "math", "Intermediate", "playlist", "Fourier series and transforms for data science and engineering."),
    ("PLqwozWPBo-FtNyPKLDPTVDOHwK12QbVsM", "Visually Explained", "math", "Beginner", "playlist", "Animated explanations of optimization, linear algebra and ML math."),

    # ---------- more deep learning & LLMs ----------
    ("PLiaHhY2iBX9hdHaRr6b7XevZtgZRa1PoU", "Neural Networks Demystified (Welch Labs)", "deep-learning", "Beginner", "course", "Short classic series building a neural network from scratch."),
    ("PLiaHhY2iBX9ihLasvE8BKnS2Xg8AhY6iV", "Learning to See (Welch Labs)", "deep-learning", "Beginner", "playlist", "Welch Labs' story-driven intro to machine learning and computer vision."),
    ("PLPz3O_BKtnTCoJlcRIrhtQ7CDewWhzI7x", "Neural Networks from Scratch (Algorithmic Simplicity)", "deep-learning", "Beginner", "playlist", "Why neural networks work, explained from first principles."),
    ("PLgtmMKe4spCPsxyMpg-sxf3EcbsFYlzPK", "AI & Machine Learning (Artem Kirsanov)", "deep-learning", "Intermediate", "playlist", "Beautifully animated explainers connecting ML and neuroscience."),
    ("PLzvYlJMoZ02Dxtwe-MmH4nOB5jYlMGBjr", "Reinforcement Learning by the Book (Mutual Information)", "deep-learning", "Intermediate", "playlist", "Sutton & Barto's RL textbook explained visually."),
    ("PLMrJAkhIeNNQe1JXNvaFvURxGY4gE9k74", "Reinforcement Learning (Steve Brunton)", "deep-learning", "Intermediate", "playlist", "Overview of reinforcement learning methods and deep RL."),
    ("PLO45-80-XKkQyROXXpn4PfjF1J2tH46w8", "MiniTorch: DIY ML Engineering (Sasha Rush)", "deep-learning", "Advanced", "course", "Build your own PyTorch-like library to understand ML engineering."),
    ("PLpZBeKTZRGPPvAyM9DM-a6W0lugCo8WfC", "Diffusion Models Explained (AI Coffee Break)", "deep-learning", "Intermediate", "playlist", "How diffusion models generate images, explained clearly."),
    ("PLdUcsPPD8lGx92jBEylh3VAERaM5d9rRT", "Flow Matching and Diffusion Models (Jia-Bin Huang)", "deep-learning", "Advanced", "playlist", "Modern generative modeling: diffusion and flow matching."),
    ("PLOspHqNVtKADfxkuDuHduUkDExBpEt3DF", "AI Fundamentals (IBM)", "deep-learning", "Beginner", "playlist", "IBM's short explainers on core AI and ML concepts."),
    ("PLpZBeKTZRGPOz2KK3J_Y3pH81NssReJ9j", "Large Language Models Explained (AI Coffee Break)", "llms", "Beginner", "playlist", "Letitia explains how LLMs work and the research behind them."),
    ("PLpZBeKTZRGPNdymdEsSSSod5YQ3Vu0sKY", "The Transformer Explained (AI Coffee Break)", "llms", "Beginner", "playlist", "Attention and transformers, step by step."),
    ("PLdUcsPPD8lGzctkUXlvcmSBL1GeoErrd5", "Modern Transformer Architecture Explained (Jia-Bin Huang)", "llms", "Intermediate", "playlist", "What changed in transformers since 2017: RoPE, GQA, MoE and more."),
    ("PLdUcsPPD8lGzEyREHXcXuqwN1pPLlMPw4", "Multimodal Foundation Models (Jia-Bin Huang)", "llms", "Intermediate", "playlist", "How vision-language and multimodal models are built."),
    ("PLO45-80-XKkT6BUKCYeBMTEqnlcpYavxq", "Flash LLM (Sasha Rush)", "llms", "Advanced", "playlist", "Short technical deep dives into how modern LLMs work."),
    ("PLvcbYUQ5t0UEK2KAGyUP7JO9K-Arct8OM", "Natural Language Processing (ritvikmath)", "llms", "Beginner", "playlist", "From word embeddings to transformers, clearly explained."),
    ("PLOspHqNVtKAC-FUNMq8qjYVw6_semZHw0", "AI Models Explained (IBM)", "llms", "Beginner", "playlist", "IBM explainers on LLMs, reasoning models, fine-tuning and more."),
    ("PLOspHqNVtKAB6AzNie7BrFhbg4dv4Gfz8", "AI Agents Explained (IBM)", "llms", "Beginner", "playlist", "How AI agents work: tools, memory, planning and multi-agent systems."),
    ("PLOspHqNVtKADc8E1JLd_kBBPdEBDdmwsR", "RAG Explained (IBM)", "llms", "Beginner", "playlist", "Retrieval-augmented generation, explained."),
    ("PLOspHqNVtKAAY8UCxA15eIK3lgE9BLc4n", "MCP Explained (IBM)", "llms", "Beginner", "playlist", "The Model Context Protocol and how agents connect to tools."),
    ("PLlrxD0HtieHj2nfK54c62lcs3-YSTx3Je", "Generative AI for Beginners (Microsoft)", "llms", "Beginner", "course", "Microsoft's free beginner course on building with generative AI."),
    ("PLlrxD0HtieHgKcRjd5-8DT9TbwdlDO-OC", "AI Agents for Beginners (Microsoft)", "llms", "Beginner", "course", "Microsoft's free beginner course on building AI agents."),
    ("PLlrxD0HtieHjYfVUpGl_-ai7D6FRBjV-d", "MCP for Beginners (Microsoft)", "llms", "Beginner", "course", "Microsoft's beginner course on the Model Context Protocol."),
    ("PLujxSBD-JXgmB1AnewzycdtUtf5YVUyzU", "Two Minute Papers: ChatGPT, GPT, Claude and more", "papers", "Beginner", "playlist", "Two Minute Papers on the latest language-model research."),
    ("PLujxSBD-JXgmoQMNJ3mt_upr7JN7pK7Cz", "Two Minute Papers: DeepMind explained", "papers", "Beginner", "playlist", "AlphaFold, AlphaGo and other DeepMind research, explained."),
]

# Free, credible learning resources outside YouTube (links open in a new tab). format: online course | hands-on | reading
EXTERNAL = [
    # AI safety & alignment
    ("bluedot-tas", "Technical AI Safety", "BlueDot Impact", "alignment", "Intermediate", "online course",
     "https://bluedot.org/courses/technical-ai-safety", "Cohort-based course on the core technical problems in AI safety."),
    ("bluedot-agi", "AGI Strategy", "BlueDot Impact", "ai-risk", "Beginner", "online course",
     "https://bluedot.org/courses/agi-strategy", "Short course on how advanced AI could go well or badly, and what to do about it."),
    ("mlsafety", "Intro to ML Safety", "Center for AI Safety (Dan Hendrycks)", "alignment", "Intermediate", "online course",
     "https://course.mlsafety.org/", "Lectures, readings and exercises on robustness, monitoring, alignment and systemic safety."),
    ("arena", "ARENA: Alignment Research Engineer Accelerator", "ARENA", "interpretability", "Advanced", "online course",
     "https://www.arena.education/", "Hands-on coding curriculum: transformers from scratch, mech interp, RL and evals."),
    ("atlas", "AI Safety Atlas", "CeSIA", "alignment", "Beginner", "reading",
     "https://ai-safety-atlas.com/", "Open textbook covering capabilities, risks, alignment, governance and evaluations."),
    ("aisafetybook", "AI Safety, Ethics & Society (textbook)", "Center for AI Safety", "ai-risk", "Beginner", "reading",
     "https://www.aisafetybook.com/", "Free textbook behind CAIS's course on catastrophic risks and governance."),
    ("dlai-quality", "Quality and Safety for LLM Applications", "DeepLearning.AI", "safety-evals", "Beginner", "online course",
     "https://www.deeplearning.ai/courses/quality-safety-llm-applications", "Short course on monitoring hallucinations, jailbreaks and data leakage."),
    ("dlai-agents-eval", "Evaluating AI Agents", "DeepLearning.AI", "safety-evals", "Intermediate", "online course",
     "https://www.deeplearning.ai/courses/evaluating-ai-agents", "Short course on building evaluations for agentic systems."),
    # AI security
    ("dlai-redteam", "Red Teaming LLM Applications", "DeepLearning.AI", "red-teaming", "Beginner", "online course",
     "https://www.deeplearning.ai/courses/red-teaming-llm-applications", "Short course on manually and automatically red-teaming LLM apps."),
    ("dlai-guardrails", "Safe and Reliable AI via Guardrails", "DeepLearning.AI", "llm-security", "Intermediate", "online course",
     "https://www.deeplearning.ai/courses/safe-and-reliable-ai-via-guardrails", "Short course on building input/output guardrails for LLM apps."),
    ("portswigger", "Web LLM attacks (labs)", "PortSwigger Web Security Academy", "prompt-injection", "Intermediate", "hands-on",
     "https://portswigger.net/web-security/llm-attacks", "Free interactive labs: exploit LLM APIs, indirect prompt injection and insecure output handling."),
    ("gandalf", "Agent Breaker (formerly Gandalf)", "Lakera", "prompt-injection", "Beginner", "hands-on",
     "https://play.lakera.ai/", "Game: hack real-world GenAI apps and agents with prompt attacks, level by level."),
    ("hackaprompt", "HackAPrompt", "Learn Prompting", "prompt-injection", "Beginner", "hands-on",
     "https://www.hackaprompt.com/", "Prompt-hacking competition and practice tracks."),
    ("grayswan", "Gray Swan Arena", "Gray Swan AI", "jailbreaks", "Intermediate", "hands-on",
     "https://app.grayswan.ai/arena", "Live jailbreaking and red-teaming competitions against frontier models."),
    ("ms-airt", "Microsoft AI Red Team guidance", "Microsoft Learn", "red-teaming", "Intermediate", "reading",
     "https://learn.microsoft.com/en-us/security/ai-red-team/", "How Microsoft red-teams AI systems: methodology, tools and lessons."),
    ("owasp-llm", "OWASP Top 10 for LLM Applications", "OWASP GenAI Security Project", "llm-security", "Beginner", "reading",
     "https://genai.owasp.org/llm-top-10/", "The standard list of the most critical LLM application risks, with mitigations."),
    ("saif", "Secure AI Framework (SAIF)", "Google", "llm-security", "Beginner", "reading",
     "https://saif.google/", "Google's framework and risk map for securing AI systems."),
    ("mitre-atlas", "MITRE ATLAS", "MITRE", "regulation", "Intermediate", "reading",
     "https://atlas.mitre.org/", "Knowledge base of adversary tactics and techniques against AI systems (ATT&CK for AI)."),
    # Policy, regulation & standards
    ("bluedot-gov", "AI Governance", "BlueDot Impact", "governance", "Beginner", "online course",
     "https://bluedot.org/courses/ai-governance", "Cohort-based course on policy levers for managing advanced AI."),
    ("nist-rmf", "NIST AI Risk Management Framework", "NIST", "regulation", "Intermediate", "reading",
     "https://www.nist.gov/itl/ai-risk-management-framework", "The US voluntary framework for managing AI risk, with playbook and profiles."),
    ("eu-ai-act", "EU AI Act Explorer", "Future of Life Institute", "regulation", "Beginner", "reading",
     "https://artificialintelligenceact.eu/", "Searchable text of the EU AI Act with summaries and implementation timeline."),
    ("iso-42001", "ISO/IEC 42001: AI management systems", "ISO", "regulation", "Intermediate", "reading",
     "https://www.iso.org/standard/81230.html", "The international standard for establishing and running an AI management system."),
    # Foundations
    ("hf-llm", "Hugging Face LLM Course", "Hugging Face", "llms", "Beginner", "online course",
     "https://huggingface.co/learn/llm-course", "Free course on transformers, fine-tuning and building with open models."),
    ("hf-agents", "Hugging Face AI Agents Course", "Hugging Face", "llms", "Intermediate", "online course",
     "https://huggingface.co/learn/agents-course", "Free course on how agents work and how to build them."),
]


def main():
    out = []
    for pid, title, topic, level, kind, desc in COURSES:
        eps, tok = [], None
        while True:
            p = dict(part="snippet", playlistId=pid, maxResults=50)
            if tok:
                p["pageToken"] = tok
            try:
                d = call("playlistItems", **p)
            except RuntimeError as e:
                print("SKIPPED (not found):", title, "-", e); d = {}
            for it in d.get("items", []):
                s = it["snippet"]
                vid = s.get("resourceId", {}).get("videoId")
                if vid and s["title"] not in ("Private video", "Deleted video"):
                    eps.append({"id": vid, "title": html.unescape(s["title"])})
            tok = d.get("nextPageToken")
            if not tok:
                break
        det = {}
        for i in range(0, len(eps), 50):
            d = call("videos", part="contentDetails,statistics,snippet", id=",".join(e["id"] for e in eps[i:i + 50]))
            for it in d.get("items", []):
                det[it["id"]] = (iso_dur(it["contentDetails"].get("duration")),
                                 int(it["statistics"].get("viewCount", 0) or 0), it["snippet"]["channelTitle"],
                                 it["snippet"].get("publishedAt", "")[:10])
        eps = [dict(e, duration_s=det[e["id"]][0], views=det[e["id"]][1], channel=det[e["id"]][2],
                    published=det[e["id"]][3]) for e in eps if e["id"] in det and det[e["id"]][0] >= 60
               and "full course" not in e["title"].lower()]   # skip compilation re-uploads of the episodes
        if not eps:
            print("EMPTY", title); continue
        chan = max(set(e["channel"] for e in eps), key=[e["channel"] for e in eps].count)
        out.append({"id": pid, "title": title, "channel": chan, "topic": topic, "level": level, "kind": kind, "desc": desc,
                    "episodes": eps, "duration_s": sum(e["duration_s"] for e in eps)})
        print(f"{title:40} {chan:24} {len(eps):3} eps  {sum(e['duration_s'] for e in eps)/3600:.1f} h")
    for eid, title, provider, topic, level, fmt, url, desc in EXTERNAL:
        if fmt == "reading":
            continue   # reading material (frameworks, standards, textbooks) is kept in the list but not shown
        out.append({"id": "ext-" + eid, "title": title, "channel": provider, "topic": topic, "level": level,
                    "kind": "course", "format": fmt, "url": url, "desc": desc, "episodes": [], "duration_s": 0})
    for c in out:
        c.setdefault("format", "video")
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
