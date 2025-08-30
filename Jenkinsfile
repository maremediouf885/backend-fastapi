pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'transfert-denrees-api'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'maremediouf885'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Récupération du code source...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installation des dépendances Python...'
                sh '''
                    python3 -m pip install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Exécution des tests unitaires...'
                sh 'python3 -m pytest tests/ -v --tb=short'
            }
            post {
                always {
                    echo 'Tests terminés'
                }
                failure {
                    echo 'ÉCHEC: Tests unitaires'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Construction de l\'image Docker...'
                sh """
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }
        
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo 'Publication sur Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', 
                                                usernameVariable: 'DOCKER_USER', 
                                                passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        docker login -u \$DOCKER_USER -p \$DOCKER_PASS
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Déploiement de l\'application...'
                sh """
                    docker stop transfert-denrees-app || echo "Conteneur non trouvé"
                    docker rm transfert-denrees-app || echo "Conteneur non trouvé"
                    docker run -d --name transfert-denrees-app -p 8000:8000 \\
                        -e DATABASE_URL="postgresql://postgres:passer123@host.docker.internal:5432/denrees_db" \\
                        -e SECRET_KEY="your-secret-key-here" \\
                        -e ALGORITHM="HS256" \\
                        -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \\
                        ${DOCKER_IMAGE}:latest
                """
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline terminé'
            sh 'docker system prune -f'
        }
        success {
            echo 'SUCCÈS: Pipeline exécuté avec succès!'
        }
        failure {
            echo 'ÉCHEC: Le pipeline a échoué'
        }
    }
}