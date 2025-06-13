# 🛍️ Chatbot de Compras com API no Azure

### 👥 Projeto realizado por: 
- **Brenda Mendes** | 202209150008
- **Ian Esteves** | 202302937314
- **Mateus Padilha** | 202308065361

Este projeto implementa um **Chatbot inteligente** integrado com uma **API hospedada no Azure**, permitindo que usuários realizem consultas e compras de produtos de forma rápida e intuitiva. A solução é sustentada por um banco de dados na nuvem, utilizando **Azure SQL** e **Cosmos DB**.

---

## 📌 Funcionalidades

### 🤖 Chatbot
O chatbot oferece as seguintes interações:
1. 🔍 **Consulta de Pedidos**  
2. 📦 **Consulta de Produtos**  
3. 📄 **Extrato de Compras**  
4. 🛒 **Compra de Produtos**

### 🌐 API (Web App no Azure)
A API fornece os seguintes endpoints:

⋆ **users**:
- ✅ **POST /users** - Cria um usuário
- ❌ **DELETE /users/{user_id}** - Deleta um usuário e todos os seus endereços e cartões
- 🔍 **GET /users/{user_id}** - Retorna um usuário pelo seu ID
   
⋆ **products**:
- ✅ **POST /products** - Cria um produto no Cosmos DB
- 🔍 **GET /products/search** - Retorna um produto 
- ❌ **DELETE /products/{product_id}** - Deleta um produto no Cosmos DB pelo seu ID
- 🔍 **GET /products/{product_id}** - Retorna um produto pelo seu ID
   
⋆ **address**:
- ✅ **POST /address/{user_id}** - Cria um endereço para o usuário informado
- ❌ **DELETE /address{user_id}/{address_id}** - Deleta um endereço específico de um usuário
- 🔍 **GET /address/{user_id}/{address_id}** - Retorna um endereço pelo ID e usuário

⋆ **credit_card**:
- 🔍 **GET /credit_card/{user_id}** - Retorna todos os cartões de crédito de um usuário
- ✅ **POST /credit_card/{user_id}** - Cadastra um cartão para um usuário
- ❌ **DELETE /credit_card/{user_id}/{card_id}** - Deleta um cartão específico de um usuário
- 🔍 **GET /credit_card/{user_id}/{card_id}** - Retorna um cartão pelo ID do cartão do usuário
- ✅ **POST /credit_card/{user_id}/{card_id}/authorize** - Autoriza uma transação de compra em um cartão de crédito do usuário

⋆ **orders**:
- ✅ **POST /orders** - Realiza uma compra
- 🔍 **GET /orders/extract/{user_id}/{card_id}/{month}** - Retorna o extrato de compras de um cartão do usuário filtrando pelo mês
- 🔍 **GET /orders/{user_id}** - Lista todos os pedidos de um usuário
- 🔍 **GET /orders/{user_id}/{pedido_id}** - Consulta um pedido pelo ID do usuário e do pedido

---

## ☁️ Arquitetura

- **Frontend**: Interface via Chatbot
- **Backend**: API REST hospedada como **Web App no Azure**
- **Banco de Dados**: 
  - 📘 **Azure Database for MySQL - Flexible Server** 
  - 🔭 **Azure Cosmos DB** 

---

## 🚀 Tecnologias Utilizadas

- **Python**
- **Flask**
- **Microsoft Bot Framework**
- **Azure Web App**
- **Azure Database for MySQL - Flexible Server**
- **Azure Cosmos DB**
- **GitHub Actions** 
