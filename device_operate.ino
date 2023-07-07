//define pin as outputs
#define R1 7
#define R2 6
#define R3 5
#define R4 4
#define R5 3
#define R6 2
#define R7 11
#define R8 10

#define C1 A5
#define C2 A4
#define C3 A3
#define C4 A2
#define C5 A1
#define C6 A0
#define C7 9
#define C8 8


void setup()
{
  	Serial.begin(9600); 
  	delay(100);
  	//Serial.println("type something");
  	
  	pinMode(A0,OUTPUT);
    pinMode(A1,OUTPUT);
    pinMode(A2,OUTPUT);
    pinMode(A3,OUTPUT);
    pinMode(A4,OUTPUT);
    pinMode(A5,OUTPUT);  
    pinMode(8, OUTPUT);
    pinMode(9, OUTPUT);
    pinMode(11, OUTPUT);
   	pinMode(10, OUTPUT);
    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);
    pinMode(5, OUTPUT);
    pinMode(6, OUTPUT);  
    pinMode(7, OUTPUT);	

  	
}

//Cols are connected as Cathode(-)
// to pass current, set LOW
void set_LED_in_Active_Row(int col, int state){
  if(col==1)digitalWrite(C1,state);
  if(col==2)digitalWrite(C2,state);
  if(col==3)digitalWrite(C3,state);
  if(col==4)digitalWrite(C4,state);
  if(col==5)digitalWrite(C5,state);
  if(col==6)digitalWrite(C6,state);
  if(col==7)digitalWrite(C7,state);
  if(col==8)digitalWrite(C8,state);		
}

//Rows are connected as cathode(-)
void selectRow(int row){
  if(row==1)digitalWrite(R1,LOW);else digitalWrite(R1,HIGH);
  if(row==2)digitalWrite(R2,LOW);else digitalWrite(R2,HIGH);
  if(row==3)digitalWrite(R3,LOW);else digitalWrite(R3,HIGH);
  if(row==4)digitalWrite(R4,LOW);else digitalWrite(R4,HIGH);
  if(row==5)digitalWrite(R5,LOW);else digitalWrite(R5,HIGH);
  if(row==6)digitalWrite(R6,LOW);else digitalWrite(R6,HIGH);
  if(row==7)digitalWrite(R7,LOW);else digitalWrite(R7,HIGH);
  if(row==8)digitalWrite(R8,LOW);else digitalWrite(R8,HIGH);
}

int image[8][8]={{0,0,0,0,0,0,0,0},
                {0,0,0,0,0,0,0,0},
                {0,0,0,0,0,0,0,0},
                {0,0,0,0,0,0,0,0},
                {0,0,0,0,0,0,0,0},
                {0,0,0,0,0,0,0,0},
                {0,0,0,0,0,0,0,0},             
				{0,0,0,0,0,0,0,0}};

//to reset the imagr matrix
void reset(int image[][8]){
	memset(image,0, 8*8*sizeof(int));
}

void offCol(){
  digitalWrite(C1,LOW);
  digitalWrite(C2,LOW);
  digitalWrite(C3,LOW);
  digitalWrite(C4,LOW);
  digitalWrite(C5,LOW);
  digitalWrite(C6,LOW);
  digitalWrite(C7,LOW);
  digitalWrite(C8,LOW);
}


//receive Serial input and change the image matrix accordingly
void receive_input(int image[][8]){
  char input;
  String row="";
  String col="";
  while(Serial.available()>0){
      input=(char)Serial.read();
    
    //to reset matrix once receive s command)  
    if (input=='s'){
    	reset(image);
        continue;
      };

      if (input=='r'){
          row+=(char)Serial.read();
      }
      else if (input=='c'){
          col+=(char)Serial.read();
      };

      if (row.length()>0 && col.length()>0){
          int row_num = atoi(row.c_str());
          int col_num = atoi(col.c_str());
          image[row_num][col_num]=1;
       	  Serial.print("row:");
          Serial.println(row_num);
          Serial.print("col:");
          Serial.println(col_num);
          Serial.println(image[row_num][col_num]);
          row="";
          col="";
      };
  };
  Serial.write('1');
  
}

void operate(){
  for(int i=0;i<8;i++){
        selectRow(i+1);
        for(int j=0;j<8;j++){
          set_LED_in_Active_Row(j+1, image[i][j]);
        };
    offCol();
      };
}


//String sparse="";

void loop()
{ 
  
  if (Serial.available()>0){
  	Serial.print("have signal coming");
    
    delay(60);
    Serial.println(Serial.available());
    receive_input(image);
  };
  
  
  operate();
  
}
