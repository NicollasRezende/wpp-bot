from typing import Dict, Any
from sqlalchemy.orm import Session

from app.db.crud.menu import CRUDMenu
from app.models.menu import Menu


# Initial menus for the application
INITIAL_MENUS: Dict[str, Dict[str, Any]] = {
    "initial": {
        "name": "initial",
        "description": "Initial menu shown after user accepts terms",
        "content": "Olá, {name}! Bem-vindo ao nosso atendimento pelo WhatsApp. Como posso ajudar você hoje?",
        "options": {
            "menu_type": "button",
            "buttons": {
                "info": {
                    "id": "info",
                    "title": "Informações Gerais",
                    "next_menu": "info"
                },
                "support": {
                    "id": "support",
                    "title": "Suporte",
                    "next_menu": "support"
                },
                "commercial": {
                    "id": "commercial",
                    "title": "Comercial",
                    "next_menu": "commercial"
                }
            }
        }
    },
    "info": {
        "name": "info",
        "description": "Information menu",
        "parent_id": 1,  # ID of initial menu
        "content": "**Informações Gerais**\n\nSelecione uma opção para saber mais:",
        "options": {
            "menu_type": "list",
            "header": "Informações",
            "footer": "Selecione uma opção",
            "button_text": "Ver opções",
            "sections": {
                "about": {
                    "title": "Sobre Nós",
                    "rows": {
                        "about_company": {
                            "id": "about_company",
                            "title": "Nossa Empresa",
                            "description": "Conheça nossa história e valores"
                        },
                        "services": {
                            "id": "services",
                            "title": "Nossos Serviços",
                            "description": "Conheça os serviços que oferecemos"
                        },
                        "location": {
                            "id": "location",
                            "title": "Localização",
                            "description": "Onde nos encontrar"
                        }
                    }
                },
                "contact": {
                    "title": "Contato",
                    "rows": {
                        "contact_info": {
                            "id": "contact_info",
                            "title": "Contatos",
                            "description": "Nossos canais de atendimento"
                        },
                        "social_media": {
                            "id": "social_media",
                            "title": "Redes Sociais",
                            "description": "Siga-nos nas redes sociais"
                        }
                    }
                }
            }
        }
    },
    "support": {
        "name": "support",
        "description": "Support menu",
        "parent_id": 1,  # ID of initial menu
        "content": "**Suporte**\n\nComo podemos ajudar você hoje?",
        "options": {
            "menu_type": "button",
            "buttons": {
                "technical": {
                    "id": "technical",
                    "title": "Suporte Técnico",
                    "next_menu": "technical_support"
                },
                "financial": {
                    "id": "financial",
                    "title": "Suporte Financeiro",
                    "next_menu": "financial_support"
                },
                "feedback": {
                    "id": "feedback",
                    "title": "Feedback",
                    "next_menu": "feedback"
                }
            }
        }
    },
    "commercial": {
        "name": "commercial",
        "description": "Commercial menu",
        "parent_id": 1,  # ID of initial menu
        "content": "**Comercial**\n\nConheça nossas soluções:",
        "options": {
            "menu_type": "list",
            "header": "Soluções",
            "footer": "Selecione uma categoria",
            "button_text": "Ver categorias",
            "sections": {
                "voice": {
                    "title": "Soluções de Voz",
                    "rows": {
                        "sip": {
                            "id": "sip",
                            "title": "SIP Server",
                            "description": "Serviço de servidor de voz SIP"
                        },
                        "call_recorder": {
                            "id": "call_recorder",
                            "title": "Gravador de Chamadas",
                            "description": "Serviço de gravação de chamadas"
                        },
                        "ip_phones": {
                            "id": "ip_phones",
                            "title": "Aparelhos IP",
                            "description": "Serviço de telefonia com aparelhos IP"
                        }
                    }
                },
                "data": {
                    "title": "Soluções de Dados",
                    "rows": {
                        "vpn": {
                            "id": "vpn",
                            "title": "VPN",
                            "description": "Serviço de rede privada virtual"
                        },
                        "firewall": {
                            "id": "firewall",
                            "title": "Firewall",
                            "description": "Serviço de proteção de rede"
                        },
                        "virtualization": {
                            "id": "virtualization",
                            "title": "Virtualização",
                            "description": "Serviço de virtualização de servidores"
                        }
                    }
                }
            }
        }
    },
    "technical_support": {
        "name": "technical_support",
        "description": "Technical support menu",
        "parent_id": 3,  # ID of support menu
        "content": "**Suporte Técnico**\n\nPor favor, descreva o problema que está enfrentando e envie uma mensagem detalhada. Nossa equipe responderá o mais breve possível.",
        "options": {
            "menu_type": "text",
            "awaiting_response": True,
            "context": {
                "awaiting_field": "technical_issue",
                "next_menu": "support_ticket_created"
            }
        }
    },
    "support_ticket_created": {
        "name": "support_ticket_created",
        "description": "Confirmation after support ticket creation",
        "parent_id": 3,  # ID of support menu
        "content": "**Ticket de Suporte Criado**\n\nAgradecemos por entrar em contato! Seu ticket de suporte foi criado com sucesso.\n\nUm de nossos especialistas analisará sua solicitação e responderá o mais breve possível.",
        "options": {
            "menu_type": "button",
            "buttons": {
                "back_to_main": {
                    "id": "back_to_main",
                    "title": "Voltar ao Menu Principal",
                    "next_menu": "initial"
                },
                "close": {
                    "id": "close",
                    "title": "Encerrar Atendimento",
                    "action": "close_conversation"
                }
            }
        }
    }
}


def create_initial_menus(db: Session, menu_crud: CRUDMenu):
    """
    Create initial menus in the database
    """
    # Dictionary to store menu ID mappings (name -> id)
    menu_ids = {}
    
    # First pass: Create all menus without parent relationships
    for menu_name, menu_data in INITIAL_MENUS.items():
        existing_menu = menu_crud.get_by_name(db, name=menu_name)
        
        if not existing_menu:
            # Create without parent_id first
            menu_data_copy = menu_data.copy()
            menu_data_copy.pop("parent_id", None)
            
            new_menu = menu_crud.create(
                db,
                obj_in=menu_data_copy
            )
            
            menu_ids[menu_name] = new_menu.id
        else:
            menu_ids[menu_name] = existing_menu.id
    
    # Second pass: Update parent relationships
    for menu_name, menu_data in INITIAL_MENUS.items():
        if "parent_id" in menu_data:
            parent_name = next((name for name, data in INITIAL_MENUS.items() 
                              if menu_ids.get(name) == menu_data["parent_id"]), None)
            
            if parent_name and parent_name in menu_ids:
                menu = menu_crud.get_by_name(db, name=menu_name)
                if menu:
                    menu_crud.update(
                        db,
                        db_obj=menu,
                        obj_in={"parent_id": menu_ids[parent_name]}
                    )
    
    return menu_ids