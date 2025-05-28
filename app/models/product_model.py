# app/models/product_model.py
class Product:
    def __init__(self, productCategory, productName, price, imageUrl, productDescription):
        self.id = str(uuid.uuid4())  # ID gerado automaticamente como uma string
        self.productCategory = productCategory  # Usado para particionar os dados
        self.productName = productName
        self.price = price
        self.imageUrl = imageUrl
        self.productDescription = productDescription

    def to_dict(self):
        return {
            "id": self.id,  # O ID será a chave de partição
            "productCategory": self.productCategory,
            "productName": self.productName,
            "price": self.price,
            "imageUrl": self.imageUrl,
            "productDescription": self.productDescription
        }