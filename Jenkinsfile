// Powered by Infostretch

timestamps {
    node ('GUI_Tests') {
        stage ('Checkout') {
            checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'henrygithub', url: 'git@github.com:HenryFBP/rivers-of-iron-mc.git']]])
        }
        stage ('Pre-build') {
            bat '''pipenv install'''
        }
        timeout(20) {
            stage ('Build') {
                // Unable to convert a build step referring to "com.cloudbees.jenkins.GitHubSetCommitStatusBuilder". Please verify and convert manually if required.        // Batch build step
                bat '''packwiz refresh'''
                bat '''pipenv run python test-with-pyautogui.py'''
            }
        }
    }
}
