/*#define KEY 8
#define DN 12
#define UP 13
#define ENGINE 9
#define WHEEL 11
#define BUZZER 10*/

/*#define KEY 2
#define DN 6
#define UP 7
#define ENGINE 3
#define WHEEL 5
#define BUZZER 4*/

#define KEY 8
#define DN 12
#define UP 9
#define ENGINE 11
#define BUZZER 10

#define HELMET_ON 0x3F
#define HELMET_OFF 0xC0

struct {
  bool up = 0;
  bool key = 0;
  bool down = 0;
  bool engine = 0;
  bool helmet = 0;
  bool buzzer = 0;
  bool throttle = 0;
}stat;

char buff[100];
uint8_t Status = 0x00;
uint8_t gear_index = 0;
uint8_t gears[6] = {0,42,84,126,168,210};

void Check_Vehicle_Status(){
  
  //check ignition key status
  if((!digitalRead(KEY))){
    delay(1);
    if(!digitalRead(KEY)){stat.key = 1;}
    else{stat.key = 0;}
  }
  else{stat.key = 0;}

  //check gear UP button status
  if(!digitalRead(UP)){
    delay(1);
    if(!digitalRead(UP)){stat.up = 1;}
    else{stat.up = 0;}
  }

  //check gear DOWN button status
  if(!digitalRead(DN)){
    delay(1);
    if(!digitalRead(DN)){stat.down = 1;}
    else{stat.down = 0;}
  }

  //check healmet status
  if(Serial.available()){
    uint8_t temp = Serial.read();
    //helmet on
    if(temp == HELMET_ON){stat.helmet = 1;}
    //helmet off
    else if(temp == HELMET_OFF){stat.helmet = 0;}
    else{stat.helmet = 0;}
  }
}

void Change_Gear_Normal(){
  //increase gear
  if(stat.up && (gear_index<5)){gear_index++;stat.up=0;}

  //decrease gear
  if(stat.down && (gear_index>0)){gear_index--;stat.down=0;}
}

void Change_Gear_Trotteled(){
  //increase gear
  if(stat.up && (gear_index<1)){gear_index++;stat.up=0;}

  //decrease gear
  if(stat.down && (gear_index>0)){gear_index--;stat.down=0;}
}

void setup(){
  Serial.begin(9600);

  pinMode(A1,OUTPUT);
  pinMode(A2,OUTPUT);
  digitalWrite(A1,LOW);
  digitalWrite(A2,LOW);
  
  //pinMode(WHEEL, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(ENGINE, OUTPUT);
  pinMode(UP,INPUT_PULLUP);
  pinMode(DN,INPUT_PULLUP);
  pinMode(KEY,INPUT_PULLUP);
}

void loop(){
  Check_Vehicle_Status();
  
  if(stat.helmet){
    stat.buzzer = 0;
    stat.throttle = 0;
    Change_Gear_Normal();
    stat.engine = stat.key;
  }
  
  else{
    stat.buzzer = 1;
    if(stat.engine){stat.throttle = 1;Change_Gear_Trotteled();}
    else{stat.engine = 0;stat.buzzer = 0;}
  }

  if((!stat.helmet)&&(stat.key)){stat.buzzer = 1;}

  if(!stat.key){stat.buzzer = 0;stat.engine = 0;}

  digitalWrite(BUZZER,stat.buzzer);
  digitalWrite(ENGINE,stat.engine);
  //analogWrite(WHEEL,gears[gear_index]);

  bitWrite(Status,7,stat.throttle);
  bitWrite(Status,6,stat.engine);
  bitWrite(Status,5,stat.key);
  Status = (Status & 0xF0) | gear_index;
  Serial.write(Status);
  //DEBUGING
  /*sprintf(buff,"UP_BUTTON: %d",stat.up);
  Serial.println(buff);
  sprintf(buff,"DOWN_BUTTON: %d",stat.down);
  Serial.println(buff);
  sprintf(buff,"KEY_BUTTON: %d",stat.key);
  Serial.println(buff);
  sprintf(buff,"ENGINE: %d",stat.engine);
  Serial.println(buff);
  sprintf(buff,"HELMET: %d",stat.helmet);
  Serial.println(buff);
  sprintf(buff,"BUZZER: %d",stat.buzzer);
  Serial.println(buff);
  sprintf(buff,"PWM: %d",gears[gear_index]);
  Serial.println(buff);
  Serial.println();*/
  delay(125);
}
