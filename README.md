# CMS
This is solely for demonstration purposes.

![drf](https://res.cloudinary.com/andinianst93/image/upload/v1703885036/Screenshot_from_2023-12-30_04-23-42_almv2r.png)

This web application works in conjunction with Next 14 as frontend and Strapi CMS.

## K8s

### Step 1: Create PV
```bash
apiVersion: v1
kind: PersistentVolume
metadata:
  name: comments-pv
  labels:
    type: comments
spec:
  capacity:
    storage: 4Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/comment_data"
```

### Step 2: Create Statefulsets
```bash
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: comments-db
  namespace: development
spec:
  selector:
    matchLabels:
      db: comments-db 
  serviceName: "comments-db"
  replicas: 1
  minReadySeconds: 10
  template:
    metadata:
      labels:
        db: comments-db
    spec:
      terminationGracePeriodSeconds: 10
      nodeSelector:
        db: postgres
      containers:
      - name: comments-db
        image: postgres:latest
        ports:
        - containerPort: 5434
          name: comments-db
        env:
        - name: POSTGRES_USER 
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: comments-db-secret
              key: password
        - name: POSTGRES_DB
          value: comments
        - name: PGDATA
          value: /var/lib/postgresql/data
        volumeMounts:
        - name: comments-pvc
          mountPath: /mnt/comment_data
  volumeClaimTemplates:
  - metadata:
      name: comments-pvc
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 2Gi


---
apiVersion: v1
kind: Service
metadata:
  name: comments-db
  namespace: development
  labels:
    app: comments-db
spec:
  ports:
    - port: 5434
      name: comments-db
  clusterIP: None
  selector:
    db: comments-db

```

### Step 4: Create Secret for the DB and Django
```bash
k create secret generic comments-secret -n development \
    --from-literal=DJANGO_SECRET_KEY=yourvalue \
    --from-literal=DEBUG=True \
    --from-literal=DJANGO_SUPERUSER_USERNAME=yourvalue \
    --from-literal=DJANGO_SUPERUSER_PASSWORD=yourvalue \
    --from-literal=DJANGO_SUPERUSER_EMAIL=yourvalue \
    --from-literal=POSTGRES_USER=yourvalue \
    --from-literal=POSTGRES_PASSWORD=yourvalue \
    --from-literal=POSTGRES_DB=comments \
    --from-literal=POSTGRES_HOST=comments-db \
    --from-literal=POSTGRES_PORT=5432

k create secret generic comments-db-secret -n development \
    --from-literal=password=yourvalue \
```

### Step 5: Create Deployment

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: comments
  labels:
    app: comments
  namespace: development
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: backend-comments
  template:
    metadata:
      labels:
        tier: backend-comments
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: tier
                operator: In
                values:
                - backend
      containers:
      - name: comments
        image: svlct/comments-demo-drf:v1
        ports:
        - containerPort: 8001
        envFrom:
        - secretRef:
            name: comments-secret
        resources:
          requests:
            cpu: "200m"
            memory: "2Gi"
          limits:
            cpu: "400m"
            memory: "4Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: comments
  namespace: development
spec:
  selector:
    tier: backend-comments
  ports:
    - protocol: TCP
      port: 8001
      targetPort: 8001
  type: ClusterIP

```