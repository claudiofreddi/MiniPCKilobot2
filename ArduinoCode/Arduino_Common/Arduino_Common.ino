#define OBJ00 0
#define OBJ01 1

#define MAX_OBJS 2

long ObjectTimeout[MAX_OBJS] = {500,5000};
long ObjectStart[MAX_OBJS] = {0,0};

bool _isDebug = true; 

int ReadObject00()
{ 
  
  delay(100);
  return random(10); 
}

int ReadObject01()
{ 
  delay(100);
  return random(10); 
}


void ExecuteCommand(String sCommandString)
 {
    sCommandString.toLowerCase();
    
    delay(1000);
    return true;
 }