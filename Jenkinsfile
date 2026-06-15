pipeline {
agent any

stages {

    stage('Checkout') {
        steps {
            git branch: 'main',
                credentialsId: 'github-ssh',
                url: 'git@github.com:MyDevopsLearnings/python-monitoring-project.git'
        }
    }

    stage('Build') {
        steps {
            sh '''
            docker build -t python-monitoring:latest .
            '''
        }
    }

    stage('Deploy') {
        steps {
            sh '''
            docker compose down || true
            docker compose up -d --build
            '''
        }
    }

    stage('Verify Deployment') {
        steps {
            sh '''
            sleep 20
            docker ps
            docker exec python-monitoring python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/metrics').read().decode('utf-8'))"
            '''
        }
    }
}

post {

    success {
        echo "Deployment Successful"
    }

    failure {
        echo "Deployment Failed"
    }
}
}
