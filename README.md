# Weld Spot Detection with Kubernetes

Этот проект позволяет обнаруживать сварочные точки на изображениях с использованием YOLO и разворачивает инфраструктуру в Kubernetes кластере на Yandex Cloud.

## Описание

Данный проект содержит Terraform модули для создания:

- Managed Kubernetes кластера с одним мастер-узлом
- Группы узлов с preemptible инстансами (прерываемые виртуальные машины)
- Сетевой инфраструктуры (VPC, подсеть, группы безопасности)
- Сервисного аккаунта с необходимыми правами
- KMS ключа для шифрования данных кластера

## Требования

- Terraform >= 1.0.0
- Yandex Cloud CLI
- Аккаунт в Yandex Cloud с активированным платежным аккаунтом

## Быстрый старт

1. Клонируйте репозиторий:
```bash
git https://github.com/GMi-s/ACID_YOLO_WSD.git
cd  ACID_YOLO_WSD
```

2. Создайте файл с переменными `infra/terraform.tfvars`:
```hcl
config = {
  zone      = "ru-central1-b"
  token     = "your-oauth-token"
  cloud_id  = "your-cloud-id"
  folder_id = "your-folder-id"
}

cluster_name         = "k8s-cluster"
network_name         = "k8s-network"
subnet_name          = "k8s-subnet"
service_account_name = "k8s-service-account"
```

3. Инициализируйте Terraform и примените конфигурацию:
```bash
cd infra
terraform init
terraform plan
terraform apply
```

## Структура проекта

```
ACID_YOLO_WSD/
├── infrastructure/
│   ├── modules/
│   │   ├── iam/              # Модуль для создания сервисного аккаунта и ролей
│   │   ├── network/          # Модуль для создания сетевой инфраструктуры
│   │   └── k8s-cluster/      # Модуль для создания Kubernetes кластера
│   ├── main.tf               # Основной файл конфигурации
│   ├── variables.tf          # Определение переменных
│   ├── outputs.tf            # Выходные значения
│   └── provider.tf           # Настройка провайдера
├── inference_image/          # Рандомное изображение с нанесённой моделью разметкой
├── k8s/                      # 
│   └── deployment.yaml       # 
├── src/                      # Основной код проекта
├── Dockerfile                # Dockerfile для сборки образа
├── docker-compose.yml        # Конфигурация Docker Compose (для локального использования)
├── cloud-init.yaml           # Конфигурация для начальной настройки виртуальной машины
├── requirements.txt          # Зависимости Python
├── README.md                 # Этот файл
└── другие файлы проекта...
```

## Настройка после развертывания

После успешного применения конфигурации:

1. Получите конфигурацию для kubectl:
```bash
yc managed-kubernetes cluster get-credentials --id $(terraform output -raw cluster_id) --external
```

2. Проверьте подключение к кластеру:
```bash
kubectl cluster-info
kubectl get nodes
```

## Создание Docker-образа и загрузка его в registry:

После успешного развертывания кластера:

1. Создайте docker-образ:
```bash
docker build -t weld-spot-detection .
```

2. Загрузите образ в registry:
```bash
docker tag weld-spot-detection cr.yandex/<registry-id>/weld-spot-detection:latest
docker push cr.yandex/<registry-id>/weld-spot-detection:latest
```

3. Получите конфигурацию для доступа к кластеру:
```bash
yc managed-kubernetes cluster get-credentials --id $(terraform output -raw cluster_id) --external
```

4. Проверьте подключение к кластеру:
```bash
kubectl cluster-info
kubectl get nodes
```

5. (Опционально) Если вы хотите использовать отдельный контекст для кластера:
```bash
# Переименовать контекст
kubectl config rename-context yc-k8s-cluster my-cluster-name

# Установить контекст по умолчанию
kubectl config use-context my-cluster-name
```

6. Проверьте текущую конфигурацию:
```bash
kubectl config get-contexts
```

### Устранение проблем с доступом

Если возникли проблемы с доступом к кластеру:

1. Проверьте статус кластера:
```bash
yc managed-kubernetes cluster list
```

2. Убедитесь, что ваш IP адрес имеет доступ к API серверу кластера:
```bash
curl -k https://$(terraform output -raw cluster_endpoint)
```

3. Проверьте корректность kubeconfig:
```bash
kubectl config view
```

## Удаление ресурсов

Для удаления всех созданных ресурсов выполните:
```bash
terraform destroy
```

## Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## Автор

Ваше Имя - [Nick Osipov](https://t.me/NickOsipov)

## Поддержка

При возникновении проблем создавайте Issue в репозитории проекта.

