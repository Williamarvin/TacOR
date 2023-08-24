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

int pixel_num = 8;

const int ROW_PINS[pixel_num] = {7, 6, 5, 4, 3, 2, 11, 10};
const int COL_PINS[pixel_num] = {A5, A4, A3, A2, A1, A0, 9, 8};
int rows = 8; // Change this value to set the number of rows
int cols = 8; // Change this value to set the number of columns
int** image;
int** depth;

void setup()
{
  	Serial.begin(9600); 
  	delay(100);
  	//Serial.println("type something");
  	
  	for(int i = 0; i < pixel_num; i++){
      pinMode(ROW_PINS[i], OUTPUT);
      pinMode(COL_PINS[i], OUTPUT);
    }

    image = new int*[rows];
    depth = new int*[rows];

    for (int i = 0; i < rows; i++) {
      image[i] = new int[cols];
      depth[i] = new int[cols];
      for (int j = 0; j < cols; j++) {
        image[i][j] = 0;
        depth[i][j] = 0;
      }
    }
}

//Cols are connected as Cathode(-)
// to pass current, set LOW
void set_LED_in_Active_Row(int col, int state){
  digitalWrite(COL_PINS[col - 1], state);
}

//Rows are connected as cathode(-)
void selectRow(int row){
  for (int i = 0; i < 8; i++) {
    digitalWrite(ROW_PINS[i], (i + 1) == row ? LOW : HIGH);
  }
}

// int image[8][8]={{0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},             
// 				        {0,0,0,0,0,0,0,0}};

// int depth[8][8] = {{0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},
//                 {0,0,0,0,0,0,0,0},             
// 				        {0,0,0,0,0,0,0,0}};

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

  while(Serial.available() > 0){
      input=(char)Serial.read();
    
    //to reset matrix once receive s command)  
    if (input=='s'){
    	reset(image);
        continue;
      };

      if (input == 'r'){
          row+=(char)Serial.read();
      }
      else if (input == 'c'){
          col+=(char)Serial.read();
      };

      if (row.length() > 0 && col.length() > 0){
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
  for(int i=0; i<8; i++){
        selectRow(i+1);
        for(int j=0; j<8; j++){
          set_LED_in_Active_Row(j+1, image[i][j]);
        };
    offCol();
    };
}


//String sparse="";

void loop()
{ 
  
  if (Serial.available() > 0){
  	Serial.print("have signal coming");
    
    delay(60);
    Serial.println(Serial.available());
    receive_input(image);
    receive_input(depth)
  };
  
  
  operate();
  for (int i = 0; i < rows; i++) {
    delete[] image[i];
    delete[] depth[i];
  }

  delete[] image;
  delete[] depth;
}
