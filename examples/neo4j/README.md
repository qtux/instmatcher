# neo4j-example
This example provides means to process affiliation nodes from a Neo4j database mainly using the [instmatcher](https://github.com/qtux/instmatcher) library.
The processing is divided into the following steps:

1. Extract: Parse and geocode an affiliation string adding the extracted data to the affiliation node.
2. Find: Search for the first matching institution using the extracted data and link it to the affiliation node.

# Deploy grobid on a CentOS 7 Machine
1. Install Git and Maven

    ```
    yum -y install git maven
    ```

2. Configure iptables to allow access to the grobid-service, for example allowing a specific IP address:

    ```
    iptables -I INPUT -p tcp --dport 8080 -s IP_ADDRESS -j ACCEPT
    ```

3. Add an unprivileged user to execute grobid

    ```
    useradd -m user -s /bin/false
    passwd --lock user
    ```

4. Switch to the user

    ```
    su -s /bin/bash user
    ```

5. Install grobid

    ```
    git clone https://github.com/kermitt2/grobid.git
    cd grobid
    mvn clean install
    ```

6. Set a grobid password

    ```
    HASHSUM=$(echo -n YOUR_PASSWORD | sha1sum | awk '{print $1}')
    sed -i "s/d033e22ae348aeb5660fc2140aec35850c4da997/${HASHSUM}/g" grobid-home/config/grobid_service.properties
    ```

7. Configure grobid

    ```
    sed -i 's/ALL/WARN/g' grobid-service/src/main/resources/log4j-jetty.properties
    ```

8. Start the grobid-service

    ```
    cd grobid-service
    mvn jetty:run-war
    # or (if you want to skip tests)
    mvn -Dmaven.test.skip=true jetty:run-war
    ```

# Run this example on another CentOS 7 Machine
1. install Git, Python3, pip and virtualenvwrapper

    ```
    yum install -y git python34 python-pip python-virtualenvwrapper
    ```

2. Add an unprivileged user to execute grobid

    ```
    useradd -m user -s /bin/false
    passwd --lock user
    ```

3. Switch to the user

    ```
    su -s /bin/bash user
    ```

4. Update virtualenvwrapper fixing a bug

    ```
    pip install --upgrade virtualenv --user
    ```

5. Edit .bashrc to use virtualenvwrapper

    ```
    echo export WORKON_HOME=~/.virtualenvs >> ~/.bashrc
    echo source /usr/bin/virtualenvwrapper.sh >> ~/.bashrc
    source ~/.bashrc
    ```

6. Install instmatcher

    ```
    git clone https://github.com/qtux/instmatcher
    cd instmatcher
    mkvirtualenv -p /usr/bin/python3.4 instmatcher
    ```

7. Install instmatcher and the example requirements inside the virtualenv

    ```
    pip install .[neo4j-example]
    ```

8. Run the neo4j example

    ```
    cd examples/neo4j
    python process.py
    ```
