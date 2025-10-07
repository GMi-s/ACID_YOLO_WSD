# Создаем кластер Kubernetes
resource "yandex_kubernetes_cluster" "k8s_cluster" {
  name       = var.cluster_name
  network_id = var.network_id
  master {
    version = "1.30"
    zonal {
      zone      = var.provider_config.zone
      subnet_id = var.subnet_id
    }
    security_group_ids = [var.security_group_id]
    public_ip = true
    maintenance_policy {
      auto_upgrade = true
    }
  }
  service_account_id      = var.service_account_id
  node_service_account_id = var.service_account_id
  release_channel = "REGULAR"
  kms_provider {
    key_id = var.kms_key_id
  }
}

# Создаем группу узлов с GPU и горизонтальным масштабированием
resource "yandex_kubernetes_node_group" "k8s_node_group" {
  cluster_id = yandex_kubernetes_cluster.k8s_cluster.id
  name       = "k8s-node-group"
  version    = "1.30"
  instance_template {
    platform_id = "standard-v2" # Используем стандартные GPU-узлы: gpu-v100, gpu-a100, gpu-p4 или gpu-t4
    network_interface {
      nat        = true
      subnet_ids = [var.subnet_id]
    }
    resources {
      memory = 16               # Увеличиваем объем памяти
      cores  = 4                # Увеличиваем количество ядер
      #gpus   = 1                # Добавляем GPU
    }
    boot_disk {
      type = "network-ssd"
      size = 64                # Увеличиваем размер диска для ML-задач
    }
    scheduling_policy {
      preemptible = true
    }
  }
  scale_policy {
    auto_scale {               # Включаем автоматическое масштабирование
      min     = 1              # Минимальное количество узлов
      max     = 8             # Максимальное количество узлов
      initial = 1              # Начальное количество узлов
    }
  }
  allocation_policy {
    location {
      zone = var.provider_config.zone
    }
  }
}