# Testing Workflow - PyTest que Replica SAM CLI Manual

## 🚀 Setup y Ejecución (Workflow Limpio)

### **Prerequisitos**
- Docker running
- AWS SAM CLI instalado
- Python 3.10+

### **1. Preparar el Entorno**

```bash
# Navegar al directorio del proyecto
cd dynamodb-crud-lambda-local

# Build SAM application
cd tests
sam build

# Verificar build exitoso
ls .aws-sam/build/  # Debería mostrar las 5 funciones Lambda
```

### **2. Iniciar DynamoDB Local (FUERA de PyTest)**

```bash
# Iniciar DynamoDB Local con network host
docker run --rm -d --name dynamodb-local --network host amazon/dynamodb-local

# Verificar que esté corriendo
curl http://localhost:8000/  # Debería responder
```

### **3. Configurar Variables de Entorno**

```bash
# En el directorio tests/
export AWS_ACCESS_KEY_ID='DUMMYIDEXAMPLE'
export AWS_SECRET_ACCESS_KEY='DUMMYEXAMPLEKEY'
export AWS_REGION='us-east-1'
```

### **4. Setup Python Environment**

```bash
# Crear y activar virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### **5. Ejecutar Tests**

```bash
# Ejecutar todos los tests
python3 -m pytest -s unit/src/test_lambda_dynamodb_local.py

# Ejecutar test específico
python3 -m pytest -s unit/src/test_lambda_dynamodb_local.py::test_lambda_create_function

# Ejecutar con verbose output
python3 -m pytest -s -v unit/src/test_lambda_dynamodb_local.py
```

### **6. Cleanup**

```bash
# Limpiar Python environment
deactivate
rm -rf venv/

# Limpiar variables
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_REGION

# Parar DynamoDB container
docker stop dynamodb-local
```

## 📊 Output Esperado (Limpio)

```
=================== test session starts ===================
platform linux -- Python 3.10.12, pytest-8.4.1
collected 7 items

unit/src/test_lambda_dynamodb_local.py 
DynamoDB Local is running on port 8000
DynamoDB Local health check passed
No existing table 'CRUDLocalTable' found - clean start confirmed

Invoking: sam local invoke CRUDLambdaInitFunction --docker-network host --event /tmp/events/temp_CRUDLambdaInitFunction_event.json
Raw SAM output: {"statusCode": 200, "body": "CRUDLocalTable"}
✓ Lambda Init function executed successfully

Invoking: sam local invoke CRUDLambdaCreateFunction --docker-network host --event /tmp/events/temp_CRUDLambdaCreateFunction_event.json  
Raw SAM output: {"statusCode": 200, "body": "{\"message\": \"Item added\", \"response\": {...}}"}
✓ Lambda Create function response: {'statusCode': 200, 'message': 'Item added'}

Invoking: sam local invoke CRUDLambdaReadFunction --docker-network host --event /tmp/events/temp_CRUDLambdaReadFunction_event.json
Raw SAM output: {"statusCode": 200, "body": "{\"name\": \"Batman\", \"Id\": \"123\"}"}
✓ Lambda Read function response: {'statusCode': 200, 'Item': {'Id': '123', 'name': 'Batman'}}

Invoking: sam local invoke CRUDLambdaUpdateFunction --docker-network host --event /tmp/events/temp_CRUDLambdaUpdateFunction_event.json
Raw SAM output: {"statusCode": 200, "body": "{\"message\": \"Item updated successfully\", \"response\": {...}}"}
✓ Lambda Update function response: {'statusCode': 200, 'message': 'Item updated successfully'}

Invoking: sam local invoke CRUDLambdaDeleteFunction --docker-network host --event /tmp/events/temp_CRUDLambdaDeleteFunction_event.json
Raw SAM output: {"statusCode": 200, "body": "{\"message\": \"Item deleted\", \"response\": {...}}"}
✓ Lambda Delete function response: {'statusCode': 200, 'message': 'Item deleted'}

✓ Full CRUD workflow completed successfully through Lambda functions
✓ Performance test completed: avg_lambda_time=1850ms, crud_operations=4

=================== 7 passed in 42.15s ===================
```

## 🛠️ Troubleshooting

### **Si DynamoDB no está disponible:**
```
SKIPPED [1] DynamoDB Local is not running on port 8000. Please start with 'docker run --rm -d --name dynamodb-local --network host amazon/dynamodb-local'
```
**Solución:** Ejecutar el comando Docker mostrado.

### **Si SAM build no está actualizado:**
```
Lambda import error: No module named 'app'. Please ensure 'sam build' has been run successfully.
```
**Solución:** 
```bash
cd tests
sam build
```

### **Si hay conflictos de puertos:**
```bash
# Verificar qué está usando el puerto 8000
sudo netstat -tlnp | grep :8000

# Matar procesos si es necesario
docker stop dynamodb-local
```

### **Si hay problemas de networking:**
- Verificar que Docker esté corriendo: `docker version`
- Verificar que `--network host` esté disponible (Linux/macOS)
- En Windows, puede necesitar configuración especial

## 🔄 Re-ejecución de Tests

Los tests ahora son **completamente idempotentes**:

```bash
# Puedes ejecutar múltiples veces sin problemas
python3 -m pytest -s unit/src/test_lambda_dynamodb_local.py
python3 -m pytest -s unit/src/test_lambda_dynamodb_local.py  # ✅ Funciona
python3 -m pytest -s unit/src/test_lambda_dynamodb_local.py  # ✅ Funciona
```

## 📝 Diferencias vs. Versión Anterior

| Aspecto | Versión Anterior | Nueva Versión |
|---------|------------------|---------------|
| **DynamoDB Management** | PyTest maneja container | Container externo |
| **Networking** | Sin `--docker-network host` | Con `--docker-network host` |
| **Clean State** | No cleanup automático | Cleanup automático al inicio |
| **Error Handling** | Muestra todos los errores | Filtra warnings harmless |
| **Idempotency** | No idempotente | Completamente idempotente |
| **Output** | Confuso con errores | Limpio y claro |

## 🎯 Validación Manual

Para verificar que PyTest replica exactamente el comportamiento manual:

```bash
# Test manual (debería funcionar igual que PyTest)
docker run --rm -d --name dynamodb-local --network host amazon/dynamodb-local

sam local invoke CRUDLambdaInitFunction --docker-network host --event ../events/lambda-init-event.json
sam local invoke CRUDLambdaCreateFunction --docker-network host --event ../events/lambda-create-event.json
sam local invoke CRUDLambdaReadFunction --docker-network host --event ../events/lambda-read-event.json
sam local invoke CRUDLambdaUpdateFunction --docker-network host --event ../events/lambda-update-event.json
sam local invoke CRUDLambdaDeleteFunction --docker-network host --event ../events/lambda-delete-event.json

# Cleanup
docker stop dynamodb-local
```

Ambos (manual y PyTest) deberían dar **exactamente los mismos resultados**.