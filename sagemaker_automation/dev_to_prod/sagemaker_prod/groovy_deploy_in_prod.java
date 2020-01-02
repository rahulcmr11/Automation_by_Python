import groovy.json.JsonOutput;
import groovy.json.JsonSlurper
@Library('github.com/releaseworks/jenkinslib')




String CODE_REPO = "https://github.build.ge.com/Talend-Power-Dev/sagemaker_prod.git"
String PARAMETERS_FILE = "prod_config_param.json"


@NonCPS
def jsonParse(def json) {
    new groovy.json.JsonSlurperClassic().parseText(json)
}

@NonCPS
def jsonString(def json) {
    new groovy.json.JsonBuilder(json).toPrettyString()
}


node {
	 
    ws("sagemaker_prod_deploy") {
		
	    def workspace = env.WORKSPACE
		 println("&&&&&&&&${workspace}")
/// this is git check out 		 
	    stage('git_checkout') {

           checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'git-code-repo', url: CODE_REPO]]]
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
	    //def jsonSlurper = new JsonSlurper() 
	    //def object = jsonSlurper.parseText(pfile)			    
		Reference_endpoint_dev = pfile.Reference_endpoint_dev    
			
			Project_name = pfile.Project_name
			//Reference_endpoint_dev = object.Reference_endpoint_dev
			gitProjectUrl = pfile.gitProjectUrl
			TargetDir = pfile.TargetDir
		        model_name = pfile.model_name
		     	variant_name = pfile.variant_name
		    	Instance_Type = pfile.Instance_Type
		    	model_execution_role = pfile.model_execution_role
		    	model_image = pfile.model_image
		    	ep_config = pfile.ep_config
            				
			println("Reference_endpoint_dev : " +Reference_endpoint_dev);
		 	println("Project_name : " +Project_name);
			println("gitProjectUrl : " +gitProjectUrl);
			println("TargetDir : " +TargetDir);
			println("ep_config : " +ep_config);
		 	println("model_name : " +model_name);
			println("variant_name : " +variant_name);
		 	println("Instance_Type : " +Instance_Type);
			println("model_execution_role : " +model_execution_role);
			println("model_image : " +model_image);
		    	//println("Policy_Json : " +Policy_Json);
		 	//println("policy_arn : " +policy_arn);
		 	
	    }
	    
////// Here comes Prod 

		stage('create_prod_bucket') 
		{

        def command = "aws s3 mb s3://ml-"+Project_name+" --region us-east-1"
		def proc = command.execute()
		def output = proc.in.text
		println(command)
		println(output)

        }

		stage('copy_git_tos3') 
		{

           //checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'git-code-repo', url: CODE_REPO]]]
		//gitProjectUrl
	    checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: TargetDir]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'git-code-repo', url: gitProjectUrl]]])
	
			
		def command = "aws s3 mv "+TargetDir+" s3://ml-"+Project_name+" --recursive  --region us-east-1"
		def proc = command.execute()
		def output = proc.in.text
		println(command)
		println(output)
        }
		
		
		
		stage('create_new_model') {
		
			aws_new_model = "aws sagemaker create-model --model-name "+Project_name+"-"+model_name+" --containers Image="+model_image+",ModelDataUrl=s3://ml-"+Project_name+"/ML_model.zip --execution-role-arn "+model_execution_role+" --region us-east-1"
			
		withEnv(["aws_new_model=$aws_new_model"]) {
		sh '''
			
			cd "$dir"
			echo $aws_new_model
			$aws_new_model
		'''
			 } 
        }
        stage('create_ep_config') {
		
			aws_ep_config = "aws sagemaker create-endpoint-config --endpoint-config-name "+Project_name+" --production-variants VariantName="+variant_name+",ModelName="+model_name+",InitialInstanceCount=1,InstanceType="+Instance_Type+" --region us-east-1"
			
		withEnv(["aws_ep_config=$aws_ep_config"]) {
		sh '''
			
			cd "$dir"
			echo $aws_ep_config
			$aws_ep_config
		'''
			 } 
        }		

	 
        

        stage("Publish NewEndpoint") {
		
        	new_end_pt = "aws sagemaker create-endpoint --endpoint-name "+Project_name+" --endpoint-config-name  "+Project_name+" --region us-east-1"
			withEnv(["new_end_pt=$new_end_pt"]) {
				
		sh '''
			echo $new_end_pt
		  $new_end_pt
		'''
		}
        }
		
		stage('json_template_overide')
		{
	    String filenew = readFile(workspace+"/sage_maker_policy.json").replaceAll('<<endpoint_name>>',Reference_endpoint_dev)
		writeFile file:workspace+"/sage_maker_policy.json", text: filenew
	    String filenew1 = readFile(workspace+"/sage_maker_policy.json").replaceAll('<<model_name>>',model_name)
			writeFile file:workspace+"/sage_maker_policy.json", text: filenew1
	    String filenew2 = readFile(workspace+"/sage_maker_policy.json").replaceAll('<<Bucket_name>>',Project_name)
			writeFile file:workspace+"/sage_maker_policy.json", text: filenew2			
	    }
		
		stage('create_policy') {

           
	    def command = "aws iam create-policy --policy-name policy-"+Project_name+" --policy-document file://"+workspace+"/sage_maker_policy.json"
	    def proc = command.execute()
		def output = proc.in.text
		          
	 	def jsonSlurper = new JsonSlurper()
          	def object = jsonSlurper.parseText(output)
	  	policy_arn = object.Policy.Arn
		println("policy_arn**-"+policy_arn)   
   
		println(command)
		println(output)
        }
	    stage('create_role') {

           
	    def command = "aws iam create-role --role-name bu-ge"+Project_name+" --assume-role-policy-document file://"+workspace+"/Role-Trust-Policy.json"
	    def proc = command.execute()
		def output = proc.in.text
		println(command)
		println(output)
        }
		stage('attach_policy_role') {

           
	    def command = "aws iam attach-role-policy --role-name bu-ge"+Project_name+" --policy-arn "+policy_arn
	    def proc = command.execute()
		def output = proc.in.text
		println(command)
		println(output)
        } //this will run after other tweaks	
        

    }
}	
