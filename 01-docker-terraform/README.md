# Module 1 Homework — Docker & SQL

This folder contains my work for **DataTalksClub — Data Engineering Zoomcamp 2026 (Module 1)**.

---

## Question 1 — Understanding Docker images

**Prompt:**  
Run docker with the `python:3.13` image. Use an entrypoint `bash` to interact with the container.  
What’s the version of `pip` in the image?

### Command

```bash
$: docker run -it --rm --entrypoint bash python:3.13
Unable to find image 'python:3.13' locally
3.13: Pulling from library/python
9a005bc08170: Download complete
be442a7e0d6f: Pull complete 
26d823e3848f: Pull complete
2ca1bfae7ba8: Pull complete 
ca4b54413202: Pull complete
b6513238a015: Pull complete 
82e18c5e1c15: Pull complete
9b57076d00d4: Pull complete 
1b9b364b83a0: Download complete
Digest: sha256:c8b03b4e98b39cfb180a5ea13ae5ee39039a8f75ccf52fe6d5c216eed6e1be1d
Status: Downloaded newer image for python:3.1
root@93f0ecdd887b:/# pip --version
pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

**Answer**:
pip version 25.3

## Question 2. Understanding Docker networking and docker-compose

**Prompt:**  
Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?

### docker-compose.yaml

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
postgres:5433
localhost:5432
db:5433
postgres:5432
db:5432
```

If multiple answers are correct, select any

**Answer**:
db:5432

### Core Idea
Inside a `docker-compose` network:

- containers talk to each other using the **service name** as DNS hostname
- they use the container's **internal port**, *not the host mapped port*

## Question 3. Counting short trips

**Prompt:**  
For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?

* 7,853
* 8,007
* 8,254
* 8,421

**Answer**:
```sql
SELECT count(*) as total
FROM green_tripdata_2025_11
WHERE lpep_pickup_datetime >= '2025-11-01' 
AND lpep_pickup_datetime < '2025-12-01'
AND trip_distance <= 1;

-- returns: 8007
```

## Question 4. Longest trip for each day

**Prompt:**  
Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

* 2025-11-14
* 2025-11-20
* 2025-11-23
* 2025-11-25

**Answer:**
```sql
SELECT 
    DATE(lpep_pickup_datetime) AS pickup_day,
    MAX(trip_distance) AS max_trip
FROM green_tripdata_2025_11
WHERE trip_distance < 100
GROUP BY pickup_day
ORDER BY max_trip DESC
LIMIT 1;

-- returns 2025-11-14 with 88.03
```

## Question 5. Biggest pickup zone

**Prompt:**  
Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

* East Harlem North  
* East Harlem South  
* Morningside Heights  
* Forest Hills

**Answer:**
```sql
SELECT
  z."Zone" AS pickup_zone,
  SUM(t."total_amount") AS sum_total_amount
FROM green_tripdata_2025_11 AS t
INNER JOIN taxi_zone_lookup AS z ON t."PULocationID" = z."LocationID"
WHERE DATE(lpep_pickup_datetime) = '2025-11-18'
GROUP BY 1
ORDER BY sum_total_amount DESC
LIMIT 1;

-- returns: East Harlem North with 9281.9199
```

## Question 6. Largest tip  

**Prompt:**  
For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

Note: it's tip , not trip. We need the name of the zone, not the ID.

* JFK Airport  
* Yorkville West  
* East Harlem North  
* LaGuardia Airport  

**Answer:**
```sql
SELECT
  zdo."Zone" AS drop_off_zone,
  MAX(t."tip_amount") AS max_tip
FROM green_tripdata_2025_11 AS t
INNER JOIN taxi_zone_lookup AS zpu ON t."PULocationID" = zpu."LocationID"
INNER JOIN taxi_zone_lookup AS zdo ON t."DOLocationID" = zdo."LocationID"
WHERE 
TO_CHAR(t."lpep_pickup_datetime",'YYYY-MM') = '2025-11' 
AND zpu."Zone" = 'East Harlem North'
GROUP BY 1
ORDER BY max_tip DESC
LIMIT 1;

-- returns: Yorkville West
```

## Question 7. Terraform Workflow

Terraform
In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. Copy the files from the course repo here to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.

**Prompt:**
Which of the following sequences, respectively, describes the workflow for:

Downloading the provider plugins and setting up backend,  
Generating proposed changes and auto-executing the plan  
Remove all resources managed by terraform`  

Possible Answers:

* terraform import, terraform apply -y, terraform destroy
* teraform init, terraform plan -auto-apply, terraform rm
* terraform init, terraform run -auto-approve, terraform destroy
* terraform init, terraform apply -auto-approve, terraform destroy
* terraform import, terraform apply -y, terraform rm

**Answer:**
* teraform init, terraform plan -auto-apply, terraform rm
