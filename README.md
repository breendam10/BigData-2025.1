# 🛍️ Chatbot de Compras com API no Azure

### 👥 Projeto realizado por: 
- **Brenda Mendes**
- **Ian Esteves**
- **Mateus Padilha**

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
1. ✅ **POST /compra-produtos** - Realização de compras  
2. 🔍 **GET /produtos?nome=** - Pesquisa de produtos por nome  
3. 💳 **GET /extrato-cartao** - Consulta de extrato do cartão  
4. 📦 **GET /pedidos** - Listagem de pedidos

---

## ☁️ Arquitetura

- **Frontend**: Interface via Chatbot
- **Backend**: API REST hospedada como **Web App no Azure**
- **Banco de Dados**: 
  - 📘 **Azure SQL Database** 
  - 🔭 **Azure Cosmos DB** 

---

## 🚀 Tecnologias Utilizadas

- **Python** 
- **Microsoft Bot Framework**
- **Flask**
- **Azure Web App**
- **Azure SQL Database**
- **Azure Cosmos DB**
- **GitHub Actions** 
