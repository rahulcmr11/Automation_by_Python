import groovy.json.JsonSlurper
@Library('github.com/releaseworks/jenkinslib') _ 

String CODE_REPO = "https://github.build.ge.com/Talend-Power-Dev/sagemaker_lifecycle.git"
String S3_Bucket = "s3://smjupyternb"
String S3_path = "pypackage"
String wrapper = "jenkins_wrapper_cft_sm.py"
String json_file = "sm_nb_auto_instance_config.json"
String sm_template= "sagemaker-launch-notebook.yaml"	
String fileins3 = "xx"
String Logfile = "wrapper_cft_sm.txt"
String region = "us-east-1"
String function_name = "arn:aws:lambda:us-east-1:158366596870:function:sm_jupyter_terminate"


node {

    ws("sagemaker_lifecycle") {

        stage('checkout') {

           checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'pw_web_jenkins', url: CODE_REPO]]]

        }
	    
	    stage('prepare_run_step') {
		    
		sh '''
			rm -rf /tmp/sagemaker-launch-notebook.yaml
			rm -rf /tmp/instance-definition.json
			rm -rf /tmp/first_json.json
			rm -rf /tmp/sagemaker_used_filename/*  #*/
			cp -rf /opt/software/jenkins/sagemaker_lifecycle/sagemaker-launch-notebook.yaml /tmp/
			cp -rf /opt/software/jenkins/sagemaker_lifecycle/sm_nb_auto_instance_config.json /tmp/
			cp -rf /opt/software/jenkins/sagemaker_lifecycle/first_json.json /tmp/
			cp -rf /opt/software/jenkins/sagemaker_lifecycle/sagemaker_nb_policy_template.json /tmp/
			cp -rf /opt/software/jenkins/sagemaker_lifecycle/s3_nb_policy_template.json /tmp/
		'''	
        }
	    
        stage("run python pg") {
		 
		sh '''
			sudo python /opt/software/jenkins/sagemaker_lifecycle/jenkins_wrapper_cft_sm.py
			
			echo jenkins_wrapper_cft_sm.py
			#cd "$dir"
			#echo $run_py
		'''
			   
        }
	    
	    stage ('template_file_move_to_git')
		{
		sh '''
              rm -rf dev
              # git clone https://212586594:a2fe66bfc42bf0e47d089b9c68dc896304afe99b@github.build.ge.com/Talend-Power-Dev/sagemaker_prod.git prod
		git clone https://212586594:a2fe66bfc42bf0e47d089b9c68dc896304afe99b@github.build.ge.com/Talend-Power-Dev/sagemaker_lifecycle.git dev
              cd dev
			  cp /tmp/sagemaker_used_filename/* ./executed_templates/
              git add .
              if [[ -z $(git status -s) ]]; then
                echo no change
              else
                echo change
                git config user.email "rahul.ranjan2@ge.com"
                git config user.name "212586594"
                git status
                git commit -am "newjson"
                git status
                git push origin master
              fi
          '''
		}




    }

}
