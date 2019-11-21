rm(list=ls(all=T))

setwd("C:/Users/212586594/Desktop/All_Imp/data Science/assignmnet/Portfolio/Portfolio_2")
### AS usual the modules whichh has to be loaded By default ################# 
x = c("ggplot2", "corrgram", "DMwR",  "randomForest", "unbalanced", "C50", "dummies", "e1071", "Information",
      "MASS", "rpart", "gbm", "ROSE", 'sampling', 'inTrees')
install.packages('dummies')
library(decisonTree)

lapply(x, require, character.only = TRUE)
#rm(x)

bike = read.csv("day.csv", header = T)# 

data_frame=bike
######Exploratory Data Analysis##################


########## changing the data type according to their behavorial ##########

data_frame$season=as.factor(data_frame$season)

data_frame$mnth=as.factor(data_frame$mnth)
data_frame$yr=as.factor(data_frame$yr)
\
data_frame$holiday=as.factor(data_frame$holiday)
data_frame$weekday=as.factor(data_frame$weekday)


data_frame$workingday=as.factor(data_frame$workingday)
data_frame$weathersit=as.factor(data_frame$weathersit)

d1=unique(data_frame$dteday)
df=data.frame(d1)
data_frame$dteday=as.Date(df$d1,format="%Y-%m-%d")

df$d1=as.Date(df$d1,format="%Y-%m-%d")

data_frame$dteday=format(as.Date(df$d1,format="%Y-%m-%d"), "%d")

data_frame$dteday=as.factor(data_frame$dteday)

str(data_frame)
###Lets  check for any null values as we have done in python same thing in R ###############################################

# 1. checking for missing value
null_val = data.frame(apply(data_frame,2,function(x){sum(is.na(x))}))




##################### Selecting correct features/columns #################


## Correlation Plot 

numeric_index = sapply(data_frame,is.numeric)

corrgram(data_frame[,numeric_index], order = F,
         upper.panel=panel.pie, text.panel=panel.txt, main = "Correlation Plot")
corr = cor(data_frame[,numeric_index], method = c("pearson", "kendall", "spearman"))

heatmap(corr, scale = "none")


## Same kind of data cloumns are removed ####

data_frame = subset(data_frame,select = -c(atemp))


####### Lets go for Random forest and Linear Regression ####################################################


###########################################
rmExcept("data_frame")
train_index = sample(1:nrow(data_frame), 0.8 * nrow(data_frame))
train_data = data_frame[train_index,]
test_data = data_frame[-train_index,]



#############     Random forest as we did in python ##########################
RF = randomForest(cnt ~ ., train_data, importance = TRUE, ntree = 200)
predictions_RF = predict(RF, test_data[,-13])
plot(RF)
################       Linear Regression            #################

#converting multilevel categorical variable into binary dummy variable
cnames= c("dteday","season","mnth","weekday","weathersit")
data_linr=data_frame[,cnames]
cnt=data.frame(data_frame$cnt)
names(cnt)[1]="cnt"
help(dummies)
data_linr= subset(data_linr,select = -c(dteday,season,mnth,weekday,weathersit))

data_linr <- dummy.data.frame(data_linr)

#data_linr= subset(data_linr,select = -c(dteday,season,mnth,weekday,weathersit))
d3 = cbind(data_linr,data_frame)
d3= subset(d3,select = -c(dteday,season,mnth,weekday,weathersit,cnt))
data_linr=cbind(d3,cnt)


#dividind data into test and train data for linear Regression ##########
train_index_linr = sample(1:nrow(data_linr), 0.8 * nrow(data_linr))
train_linr = data_linr[train_index_linr,]
test_linr = data_linr[-train_index,]

#Linear regression model predictions ###########
linear_model = lm(cnt ~., data = train_linr)
linear_predictions = predict(linear_model,test_linr[,-64])


summary(linear_model)

#######  Now same as we did in Python finding out the Mean Absolute Percentage Error ###############


MAPE = function(y, yhat){
  mean(abs((y - yhat)/y))*100
}
MAPE(test[,12], predictions_DT)

MAPE(test[,12], predictions_RF)

MAPE(test_lr[,64],  predictions_LR)



##########extacting predicted values output from Random forest model######################
results <- data.frame(test, pred_cnt = predictions_RF)

write.csv(results, file = 'RF output R .csv', row.names = FALSE, quote=FALSE)

############################################################################################









