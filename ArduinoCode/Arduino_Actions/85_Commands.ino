
void ExecuteCommand(String sCommandString)
 {
    sCommandString.toLowerCase();
    
     if (!_optimize) Serial.println("[" + sCommandString + "]");

    // Motors Commands
    if (sCommandString == CMD_FW)  { MyRobot_Motors.RunFw(CMD_FW_TIMEOUT);    return;   } 
    if (sCommandString == CMD_BW)  { MyRobot_Motors.RunBw(CMD_BW_TIMEOUT);    return;   } 
    if (sCommandString == CMD_ROT)  { MyRobot_Motors.Rotate(1,CMD_ROT_TIMEOUT);    return;   } 

    if (sCommandString == CMD_ROTB)  { MyRobot_Motors.Rotate(-1,CMD_ROT_TIMEOUT);    return;   } 
    if (sCommandString == CMD_STOP)  { MyRobot_Motors.Stop();    return;   } 
    if (sCommandString == "rotfast")  { MyRobot_Motors.Rotate(1,0);    return;   } 
    if (sCommandString == "rotfastb")  { MyRobot_Motors.Rotate(-1,0);    return;   } 

    if (sCommandString == "hspeed") { MyRobot_Motors.HighSpeed();    return;   }
    if (sCommandString == "lspeed") { MyRobot_Motors.LowSpeed();    return;   }

    if (sCommandString == "r0a")  MyRobot_Rele.ReleSetStatus(0,true,0);
    if (sCommandString == "r0s")  MyRobot_Rele.ReleSetStatus(0,false,0);
    if (sCommandString == "r1a")  MyRobot_Rele.ReleSetStatus(1,true,0);
    if (sCommandString == "r1s")  MyRobot_Rele.ReleSetStatus(1,false,0);
    if (sCommandString == "r2a")  MyRobot_Rele.ReleSetStatus(2,true,0);
    if (sCommandString == "r2s")  MyRobot_Rele.ReleSetStatus(2,false,0);
    if (sCommandString == "r3a")  MyRobot_Rele.ReleSetStatus(3,true,0);
    if (sCommandString == "r3s")  MyRobot_Rele.ReleSetStatus(3,false,0);
    if (sCommandString == "r4a")  MyRobot_Rele.ReleSetStatus(4,true,0);
    if (sCommandString == "r4s")  MyRobot_Rele.ReleSetStatus(4,false,0);

    if (sCommandString == "l0a")  MyRobot_Led.turn_led(0,true);
    if (sCommandString == "l0s")  MyRobot_Led.turn_led(0,false);
    if (sCommandString == "l1a")  MyRobot_Led.turn_led(1,true);
    if (sCommandString == "l1s")  MyRobot_Led.turn_led(1,false);
    if (sCommandString == "l2a")  MyRobot_Led.turn_led(2,true);
    if (sCommandString == "l2s")  MyRobot_Led.turn_led(2,false);
    if (sCommandString == "l3a")  MyRobot_Led.turn_led(3,true);
    if (sCommandString == "l3s")  MyRobot_Led.turn_led(3,false);

    // SINGLE POWER COMMANDS
    if (sCommandString == "main_power_on") MyRobot_Rele.MasterSupply(true, 0); 
    if (sCommandString == "main_power_off") MyRobot_Rele.MasterSupply(false, 0); 
    if (sCommandString == "motor_power_on") MyRobot_Rele.Arduino01MotorsSupply(true,0);
    if (sCommandString == "motor_power_off") MyRobot_Rele.Arduino01MotorsSupply(false,0);
  
    // Power Commands
    if (sCommandString == "switch_on") MyRobot_Rele.Switch_Arduino_And_Motors(true);
    if (sCommandString == "switch_off")  MyRobot_Rele.Switch_Arduino_And_Motors(false);


  
  }  
