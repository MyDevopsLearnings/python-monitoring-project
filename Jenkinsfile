pipeline {
agent any

stages {

    stage('Checkout') {
        steps {
            git branch: 'main',
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
            sleep 15

            curl -f http://localhost:5000/health

            docker ps
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
