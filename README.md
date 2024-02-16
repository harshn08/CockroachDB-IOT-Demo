# CockroachDB IOT multi-region demo

This demo demonstrates how CockroachDB is suited for an IOT use-case to track configuration/status data as well as sensor/telemetry information which are transactional workloads which require consistency as well as an always-on/surveive anything database with multi-region capabilities to keep data close to the source for improved performance and compliance. In this demo we use  multi-region tables (Global, Regional, Regional-by-row) for their benefits based on how the application interacts with the database.

# Walkthrough of the demo
## Setup
### Database Setup

This demo requires CockroachDB to be setup in multiple regions and use the multi-region regions. It needs to be setup to survive a region failure. Although this demo and readme is based on CockroachDB Serverless Multi-region, you can also use CockroachDB Self Hosted, Dedicated or Serverless for the demo. The CockroachDB Serverless cluster has been setup in the following regions on Google Cloud Platform: us-central1(PRIMARY REGION), us-east1, us-west2

![](/docs/cockroachdbcloud-multiregion.png)

**Create Tables and Load database with demo data**

Assuming you are using a cloud instance, eg, a linux ec2 machine, configure git and clone the repo:

```
sudo yum install -y git
git clone https://github.com/harshn08/CockroachDB-IOT-Demo.git
```

To create the Tables use the import_fleet.sql. Go to the git directory and run the following command:

```
cat import_fleet.sql | cockroachd sql --url "postgresql://<user>:<password>@<hostname>:26257/movr_demo?sslmode=verify-full"
```

To load the demo data, you need to make edits to the fleet_datagen.py file and configure the database connection parameters. After thats done, make sure you have your machine configured with python and pip and any additional requirements installed. If you are running this on cloud instances, eg, a linux ec2 machine, run the following commands to install python and other dependencies:

```
sudo yum install -y python3
sudo yum install -y python3-pip
sudo pip3 install psycopg2-binary
sudo pip3 install faker
sudo pip3 install datetime
```
After thats done run the configured fleet_datagen.py file using the following command:

```
python fleet_datagen.py
```

Depending on your instance, it may take some time to generate the data for the demo.

### CockroachDB Data Model

Here is how we have the database setup for this demo:

![](/docs/cockroachdbcloud-fleet-datamodel.png)

### Node.js App Setup

You can setup the node.js app on your local machine or on a cloud instances you created to simulate the data. For this example we have chosen the latter option but the steps to set that up remain the same. First, configure the app_fleet.js file with the connection parameters to the CockroachDB database. Next run the following commands to configure your environment for the Node.js application:

```
sudo yum install -y npm
sudo yum install -y nodejs
sudo npm install express
sudo npm install ejs
sudo npm install pg
```

Once the dependencies are successfully installed. You can start the Node.js app server by running the following command:

```
node app_fleet.js
```

And you should see an output that says:

````
Server running at http://localhost:3000
````

If you are running the app locally, you can open 'http://localhost:3000' on your browser window to see the app. If you are running this on a cloud instance, then replace localhost with the public IP of the instance: 'http://<public-ip-of-cloud-instance>:3000' and open it in your browser window.

This is what it will look like

![](/docs/fleettracker-app-homepage.png)

### Simulating the demo

Next, create a virtual instance in three diffrerent regions that correspond with the three regions of your database. It doesn't have to be exactly the same regions in case you are using a different cloud provider than where your database was setup but as long as its close enough it works for the demo. The reason why we are taking this approach is because we want to simulate the data from each of those regions to get it to resemble a real workload. 

On each of those instances, download the git repo and configure them with the required dependencies:

```
sudo yum install -y git
git clone https://github.com/harshn08/CockroachDB-IOT-Demo.git
sudo yum install -y python3
sudo yum install -y python3-pip
sudo pip3 install psycopg2-binary
sudo pip3 install faker
sudo pip3 install datetime
```

There are 3 simulator files in the repo, one corresponding to each region. Configure the simulator files(eg: fleet_simulator_west.py) with the database connection parameters. Once that is complete, you can start the corresponding simulator files in the instances in the corresponding regions using the following command:

```
python fleet_simulator_west.py
```

And here is what a sample output looks like when the simulator is running as intended:

```
('Time:', datetime.datetime(2024, 1, 5, 12, 37))
('Vehicle ID:', '5c02f053-72ec-4eeb-9753-74b8ebb72880')
Location: Lat=34.1639906929, Long=-116.292280784
('Diagnostics:', 84.89933271142556, 19.50554584374339, 9.674146080155754, 31.4972843867317, 3601, 7.702416032096549, 15.654423016111348)
()
('Time:', datetime.datetime(2024, 1, 5, 12, 45))
('Vehicle ID:', '5c02f053-72ec-4eeb-9753-74b8ebb72880')
Location: Lat=34.5096449651, Long=-116.156533782
('Diagnostics:', 79.26538480694613, 70.31072589051519, 97.4415201071555, 31.272561923073486, 737, 59.848557079794496, 15.148076593177777)
()
....
....
```

At the same time you can track the movement of the markers of the vehicles on the app and when you click on one of the markers it will get you detailed diagnostic information for the vehicle.

![](/docs/fleettracker-app-dashboard.png)


