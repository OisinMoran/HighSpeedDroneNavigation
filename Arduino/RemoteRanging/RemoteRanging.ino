// Please read the ready-to-localize tuturial together with this example.
// https://www.pozyx.io/Documentation/Tutorials/ready_to_localize

#include <Pozyx.h>
#include <Pozyx_definitions.h>
#include <Wire.h>

////////////////////////////////////////////////
////////////////// PARAMETERS //////////////////
////////////////////////////////////////////////

uint8_t num_anchors = 4;                                    // the number of anchors
uint16_t remote_tag = 0x6F28;
uint16_t anchors[4] = {0x600A, 0x602B, 0x6030, 0x602E};     // the network id of the anchors: change these to the network ids of your anchors.
int32_t heights[4] = {740, 840, 700, 1200};                 // anchor z-coordinates in mm
boolean bProcessing = true;                                 // set this to true to output data for the processing sketch         

// only required for manual anchor calibration. Please change this to the coordinates measured for the anchors
int32_t anchors_x[4] = {0, 1500, -20, 1500};                // anchor x-coorindates in mm
int32_t anchors_y[4] = {0, 0, 2500, 2480};                  // anchor y-coordinates in mm

////////////////////////////////////////////////

void setup(){
  Serial.begin(115200);
  
  if(Pozyx.begin() == POZYX_FAILURE){
    Serial.println(F("ERROR: Unable to connect to POZYX shield"));
    Serial.println(F("Reset required"));
    delay(100);
    abort();
  }
  
  Serial.println(F("----------POZYX POSITIONING V1.0----------"));
  Serial.println(F("NOTES:"));
  Serial.println(F("- No parameters required."));
  Serial.println();
  Serial.println(F("- System will auto start calibration"));
  Serial.println();
  Serial.println(F("- System will auto start positioning"));
  Serial.println(F("----------POZYX POSITIONING V1.0----------"));
  Serial.println();
  Serial.println(F("Performing auto anchor calibration:"));

  // clear all previous devices in the device list
  Pozyx.clearDevices(remote_tag);

//  int status = Pozyx.doAnchorCalibration(POZYX_2_5D, 10, num_anchors, anchors, heights);
//  if (status != POZYX_SUCCESS){
//    Serial.println(status);
//    Serial.println(F("ERROR: calibration"));
//    Serial.println(F("Reset required"));
//    delay(100);
//    abort();
//  }
  
  // if the automatic anchor calibration is unsuccessful, try manually setting the anchor coordinates.
  // fot this, you must update the arrays anchors_x, anchors_y and heights above
  // comment out the doAnchorCalibration block and the if-statement above if you are using manual mode
  SetAnchorsManual(remote_tag);
  Pozyx.setSelectionOfAnchors(POZYX_ANCHOR_SEL_AUTO, 4, remote_tag);

  printCalibrationResult(remote_tag);
  delay(3000);

  Serial.println(F("Starting positioning: "));

}

void loop(){
  
  coordinates_t position;  
  int status = Pozyx.doRemotePositioning(remote_tag, &position, POZYX_3D);
  int16_t heading_raw;
  status &= Pozyx.regRead(POZYX_EUL_HEADING, (uint8_t*)&heading_raw, sizeof(int16_t));
  //int status = Pozyx.doPositioning(&position, POZYX_2_5D, 1000);
 
  if (status == POZYX_SUCCESS)
  {
    // print out the result
    if(!bProcessing){
      printCoordinates(position);
    }else{    
      printCoordinatesProcessing(position);
    }
  }
}

// function to print the coordinates to the serial monitor
void printCoordinates(coordinates_t coor){
  
  Serial.print("x_mm: ");
  Serial.print(coor.x);
  Serial.print("\t");
  Serial.print("y_mm: ");
  Serial.print(coor.y);
  Serial.print("\t");
  Serial.print("z_mm: ");
  Serial.print(coor.z);
  Serial.println(); 
}

// function to print out positoining data + ranges for the processing sketch
void printCoordinatesProcessing(coordinates_t coor){
  
  // get the network id and print it
  //uint16_t network_id;
 // Pozyx.getNetworkId(&network_id);
  
  Serial.print("POS,0x");
  Serial.print(remote_tag,HEX);
  Serial.print(",");
  Serial.print(coor.x);
  Serial.print(",");
  Serial.print(coor.y);
  Serial.print(",");
  Serial.print(coor.z);
  Serial.print(",");
  
  // get information about the positioning error and print it
  pos_error_t pos_error;
  Pozyx.getPositionError(&pos_error, remote_tag);
    
  Serial.print(pos_error.x);
  Serial.print(",");
  Serial.print(pos_error.y);
  Serial.print(",");
  Serial.print(pos_error.z);
  Serial.print(",");
  Serial.print(pos_error.xy);
  Serial.print(",");
  Serial.print(pos_error.xz);
  Serial.print(",");
  Serial.print(pos_error.yz); 
  
  // read out the ranges to each anchor and print it 
  for (int i=0; i < num_anchors; i++){
    device_range_t range;
    Pozyx.getDeviceRangeInfo(anchors[i], &range, remote_tag);
    Serial.print(",");
    Serial.print(range.distance);  
    Serial.print(",");
    Serial.print(range.RSS); 
  }
  Serial.println();
}

// print out the anchor coordinates (also required for the processing sketch)
void printCalibrationResult(uint16_t remote_id){
  uint8_t list_size;
  int status;

  status = Pozyx.getDeviceListSize(&list_size, remote_id);
  Serial.print("list size: ");
  Serial.println(status*list_size);
  
  if(list_size == 0){
    Serial.println("Calibration failed.");
    Serial.println(Pozyx.getSystemError(remote_id));
    return;
  }
  
  uint16_t device_ids[list_size];
  status &= Pozyx.getDeviceIds(device_ids,list_size, remote_id);
  
  Serial.println(F("Calibration result:"));
  Serial.print(F("Anchors found: "));
  Serial.println(list_size);
  
  coordinates_t anchor_coor;
  for(int i=0; i<list_size; i++)
  {
    
    Serial.print("ANCHOR,");
    Serial.print("0x");
    Serial.print(device_ids[i], HEX);
    Serial.print(",");    
    status = Pozyx.getDeviceCoordinates(device_ids[i], &anchor_coor, remote_id);
    Serial.print(anchor_coor.x);
    Serial.print(",");
    Serial.print(anchor_coor.y);
    Serial.print(",");
    Serial.println(anchor_coor.z);
    
  }    
}

// function to manually set the anchor coordinates
void SetAnchorsManual(uint16_t remote_id){
 
 int i=0;
 for(i=0; i<num_anchors; i++){
   device_coordinates_t anchor;
   anchor.network_id = anchors[i];
   anchor.flag = 0x1; 
   anchor.pos.x = anchors_x[i];
   anchor.pos.y = anchors_y[i];
   anchor.pos.z = heights[i];
   Pozyx.addDevice(anchor, remote_id);
 }
}
