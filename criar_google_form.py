#!/usr/bin/env python3
"""
Script para criar um Google Forms com perguntas estratégicas de briefing.
Requer autenticação Google e bibliotecas: google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def create_form():
    """Cria um Google Forms com as perguntas de briefing estratégico."""

    # Autenticação
    auth.authenticate_user()
    forms_service = build("forms", "v1")
    drive_service = build("drive", "v3")

    # Definição do formulário
    form_title = "Briefing Estratégico - Estratégia Social Media"
    form_description = "Essas perguntas vão me ajudar a criar conteúdos alinhados com a sua essência e estratégia. Responda com sinceridade para que possamos potencializar sua presença nas redes sociais! 🚀"

    # Criar formulário vazio
    form_body = {
        "info": {
            "title": form_title,
            "description": form_description,
        }
    }

    form = forms_service.forms().create(body=form_body).execute()
    form_id = form["formId"]

    print(f"✅ Formulário criado! ID: {form_id}")

    # Definição das perguntas
    questions = [
        {
            "title": "Qual seu nome e da sua empresa?",
            "type": "SHORT_ANSWER",
            "required": True,
        },
        {
            "title": "Por qual motivo seu negócio existe? (Qual é sua missão?)",
            "description": "Fale sobre o propósito e impacto que você deseja gerar",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Descreva seus principais produtos/serviços",
            "description": "Seja específico e destaque diferenciais",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Quem é seu cliente ideal? Descreva características importantes",
            "description": "Idade, classe social, comportamento, problemas que enfrenta...",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Como você gostaria de ser visto no Instagram?",
            "description": "Que posição, título ou autoridade você deseja ter?",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Quais tipos de conteúdos você gostaria de abordar?",
            "description": "Exemplos: trajetória, dicas práticas, desafios, cursos, casos de sucesso...",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Quais tipos de conteúdos você NÃO gostaria de abordar?",
            "description": "Temas a evitar por convicção pessoal ou posicionamento",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Você tem facilidade de gravar vídeos?",
            "description": "Os roteiros serão adaptados conforme seu nível de conforto",
            "type": "MULTIPLE_CHOICE",
            "options": [
                "Sim, me sinto à vontade",
                "Mais ou menos",
                "Tenho dificuldade"
            ],
            "required": True,
        },
        {
            "title": "Cite perfis/pessoas que você tem como referência de posicionamento",
            "description": "Influenciadores, empresários ou marcas que você admira",
            "type": "PARAGRAPH",
            "required": True,
        },
        {
            "title": "Conte brevemente sua história: Como começou tudo? Quais foram os principais desafios?",
            "description": "Esse é o storytelling que usaremos. Seja genuíno!",
            "type": "PARAGRAPH",
            "required": True,
        },
    ]

    # Adicionar perguntas ao formulário
    update_request = []

    for idx, question in enumerate(questions):
        create_item_request = {
            "createItem": {
                "item": {
                    "title": question["title"],
                    "description": question.get("description", ""),
                    "questionItem": {
                        "question": {
                            "required": question["required"],
                            "questionType": question["type"],
                        }
                    },
                },
                "location": {"index": idx},
            }
        }

        # Para múltipla escolha, adicionar as opções
        if question["type"] == "MULTIPLE_CHOICE":
            options = [
                {"value": opt} for opt in question["options"]
            ]
            create_item_request["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                "type": "RADIO",
                "options": options,
            }
            # Remover questionType para múltipla escolha
            del create_item_request["createItem"]["item"]["questionItem"]["question"]["questionType"]

        update_request.append(create_item_request)

    # Enviar update com todas as perguntas
    batch_update_request = {
        "requests": update_request
    }

    response = forms_service.forms().batchUpdate(
        formId=form_id,
        body=batch_update_request
    ).execute()

    print(f"✅ {len(questions)} perguntas adicionadas!")

    # Obter URL do formulário
    form_response = forms_service.forms().get(formId=form_id).execute()
    form_url = form_response.get("responderUri")

    print(f"\n🎉 Formulário criado com sucesso!")
    print(f"🔗 Link do formulário: {form_url}")
    print(f"\n📋 Próximos passos:")
    print(f"1. Compartilhe o link com seus clientes")
    print(f"2. Peça para preencherem antes da reunião no Google Meet")
    print(f"3. Revise as respostas para a reunião!")

    return form_url

if __name__ == "__main__":
    create_form()
