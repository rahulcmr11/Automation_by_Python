import groovy.json.JsonOutput;
import groovy.json.JsonSlurper
@Library('github.com/releaseworks/jenkinslib')




String CODE_REPO = "https://github.build.ge.com/Talend-Power-Dev/sagemaker_deploy.git"
String PARAMETERS_FILE = "parameters/config_param.json"


@NonCPS
def jsonParse(def json) {
    new groovy.json.JsonSlurperClassic().parseText(json)
}

@NonCPS
def jsonString(def json) {
    new groovy.json.JsonBuilder(json).toPrettyString()
}


node {
	 
    ws("sagemaker_deploy") {
		
	    def workspace = env.WORKSPACE
		 println("&&&&&&&&${workspace}")
/// this is git check out 		 
	    stage('git_checkout') {
///// changes 
		     sh '''
			     # echo "ok1*******************"
			     echo  "ok2*******************"
			'''     
           checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'pw_web_jenkins', url: CODE_REPO]]]
		def scriptDir = getClass().protectionDomain.codeSource.location.path
		    println("###########################"+System.getProperty("user.dir"));
		    println("xxxxxxxx"+scriptDir)
			    //println("xxxxxxxx"+ws)
        }
		 

	    stage('Generate Config Params') {
/// This to read the config params 
	    SELECTED_PARAMETERS_FILE = PARAMETERS_FILE
            SELECTED_CF_TEMPLATE_FILE = SELECTED_PARAMETERS_FILE


            def pfile = jsonParse(readFile(SELECTED_PARAMETERS_FILE))

            for (int i = 0; i < pfile.size(); i++) {

                
               	if (pfile[i].ParameterKey.equalsIgnoreCase("Reference_endpoint_dev")) {
                    Reference_endpoint_dev = pfile[i].ParameterValue
                }
		if (pfile[i].ParameterKey.equalsIgnoreCase("gitProjectUrl")) {
                    gitProjectUrl = pfile[i].ParameterValue
                }
		if (pfile[i].ParameterKey.equalsIgnoreCase("Project_name")) {
                    Project_name = pfile[i].ParameterValue
                }
		if (pfile[i].ParameterKey.equalsIgnoreCase("TargetDir")) {
                    TargetDir = pfile[i].ParameterValue
                }
		if (pfile[i].ParameterKey.equalsIgnoreCase("Policy_Json")) {
                    Policy_Json = pfile[i].ParameterValue
                }
		    if (pfile[i].ParameterKey.equalsIgnoreCase("policy_arn")) {
                    policy_arn = pfile[i].ParameterValue
                }

            }
            				
			println("Reference_endpoint_dev : " +Reference_endpoint_dev);
		 	println("Project_name : " +Project_name);
			println("gitProjectUrl : " +gitProjectUrl);
			println("TargetDir : " +TargetDir);
		    	println("Policy_Json : " +Policy_Json);
		 	println("policy_arn : " +policy_arn);
		 	println("aws sagemaker describe-endpoint --endpoint-name "+Reference_endpoint_dev+" --region us-east-1")
	    }

	stage('describe_end_point')
	
//// If end point exist and in service then do other steps 
	{
	    def command = "aws sagemaker describe-endpoint --endpoint-name "+Reference_endpoint_dev+" --region us-east-1"
           def proc = command.execute()
           proc.waitFor() 
           def output = proc.in.text
	  def jsonSlurper = new JsonSlurper()
          def object = jsonSlurper.parseText(output) 
	  ep_config = object.EndpointConfigName
	  status = object.EndpointStatus
	   println("****************"+ep_config)
	   println("****************"+status)
	println('ok')
				    
	}
	
	if (status=='InService')
		{
    println("yes $Reference_endpoint_dev InService")
		//// Describe end point config 
		
		stage('describe_epconfig')
		{
	def command = "aws sagemaker describe-endpoint-config --endpoint-config-name "+ep_config+" --region us-east-1"
	println(command)
	def proc = command.execute()
           proc.waitFor() 
           def output = proc.in.text
	  def jsonSlurper = new JsonSlurper()
          def object = jsonSlurper.parseText(output)
	  model_name = object.ProductionVariants.ModelName[0]
	  variant_name = object.ProductionVariants.VariantName[0]
	  Instance_Type=object.ProductionVariants.InstanceType[0]
	  println("*************"+model_name)
	  
		}
		
		//////////// Get Model Arn and image 
		
		stage('get_image_arn_model')
		{
			
		def command = "aws sagemaker describe-model --model-name "+model_name+" --region us-east-1"
		println(command)
		def proc = command.execute()
        proc.waitFor() 
        def output = proc.in.text
		def jsonSlurper = new JsonSlurper()
        def object = jsonSlurper.parseText(output)
		model_execution_role = object.ExecutionRoleArn
		//get model image
		if (object.keySet().contains('Containers'))
		{
			model_image = object.Containers.Image
		}
		else
		{
			model_image = object.PrimaryContainer.Image
		}		
			
	  //model_image = object.Containers.Image[0]
	  println(model_execution_role)
	  println(model_image)
	  
	  println(output)
	
	
	} 

////////////// Generate Config paramaters

	stage('Generate Config Params')
	{
		def json = JsonOutput.toJson([Project_name: Project_name, Reference_endpoint_dev: Reference_endpoint_dev, gitProjectUrl: gitProjectUrl, TargetDir: TargetDir, ep_config: ep_config, model_name: model_name, variant_name: variant_name, Instance_Type: Instance_Type, model_execution_role: model_execution_role, model_image: model_image])
		
		/// writing a new json
		
		new File("${workspace}/prod_config_param.json").write(json)
		
	}	
	stage ('file_created_to_git')
		{
		sh '''
              rm -rf prod
              # git clone https://212586594:db4f94d51a80de90bfe565a706b27be7f040fe87@github.build.ge.com/Talend-Power-Dev/sagemaker_prod.git prod
		git clone https://github.build.ge.com/Talend-Power-Dev/sagemaker_prod.git prod
              cd prod
			  cp ../prod_config_param.json ./
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
		
	else 
	{
			println("The endpoint "+Reference_endpoint_dev+" is not in service ")
	}
/* this is for PROD Git 
	    {
	    String filenew = readFile(workspace+"/sage_maker_policy.json").replaceAll('<<endpoint_name>>','endpointname')
		writeFile file:workspace+"/sage_maker_policy.json", text: filenew
	    String filenew1 = readFile(workspace+"/sage_maker_policy.json").replaceAll('<<model_name>>','modelname')
			writeFile file:workspace+"/sage_maker_policy.json", text: filenew1
	    String filenew2 = readFile(workspace+"/sage_maker_policy.json").replaceAll('<<Bucket_name>>','bucket')
			writeFile file:workspace+"/sage_maker_policy.json", text: filenew2			
	    } */
    
	    
    }
}	
