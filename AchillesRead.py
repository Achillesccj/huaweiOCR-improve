# -*- coding:utf-8 -*-
# Copyright 2018 Huawei Technologies Co.,Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License.  You may obtain a copy of the
# License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations under the License.
#
# sdk reference linking：https://support.huaweicloud.com/sdkreference-ocr/ocr_04_0001.html

from HWOcrClientAKSK import HWOcrClientAKSK
import os
import math
import json

def readnote_request():
    """
    AK SK demo code
    """
    #设置华为账号相关信息，使用AKSK的方式进行调用
    AK = "AZEU6SJSZ9BMGV7XMEXD"  # AK from authentication.
    SK = "C107IKj0O3m35QI1JthUEJXA261IP6LLxq2eMexE"  # SK from authentication.
    region = "cn-north-4"  # http region information.
    
    #选择general-text的方式，说明我们选择的是通用的文本识别
    req_uri = "/v1.0/ocr/general-text"
    
    #存储笔记的路径
    note_path="C:/Achillesccj/Work/AI/1_read/cloud-ocr-sdk-python-1.0.4/test"
    out_path="C:/Achillesccj/Work/AI/1_read/cloud-ocr-sdk-python-1.0.4/test/note.txt"
    
    imgs_names=[y for y in os.listdir(note_path+'/') if '.jpg' in y]
    print(imgs_names)
    
    option = {}
    
    try:
        ocr_client = HWOcrClientAKSK(AK, SK, region)  # Initialize the ocr_client.
        
        #以追加方式打开文档,清空上一次的内容
        fo = open(out_path, "a")
        fo.seek(0)
        fo.truncate()
                
        #建立循环，每张图片进行一次识别、写入到text文档中
        for i in range(len(imgs_names)):
            img_path = note_path+'/'+imgs_names[i]
            
            #进行单张图片的识别和读取
            response = ocr_client.request_ocr_service_base64(req_uri,img_path, option)  # Call the OCR API to recognize image.
            
            response_cal(response,out_path)
           
            
        fo.close()
             
        
    except ValueError as e:
        print(e)
   
 
def response_cal(response,out_path):
    
    resultDict = json.loads(response.text)
    fo = open(out_path, "a")
    
    #基于OCR识别输出的格式，把结果赋予不同的变量
    result = resultDict["result"]
    words_block_count = result["words_block_count"]
    words_block_list=result["words_block_list"]
    height=[0 for x in range(0,words_block_count)]
    temp=[0 for x in range(0,words_block_count)]
    length=[0 for x in range(0,words_block_count)]
    center=[0 for x in range(0,words_block_count)]
    slop=[0 for x in range(0,words_block_count)]
    flag=[1 for x in range(0,words_block_count)]
    #把文本中的words都提取出来，并以追加的方式写入文件中
    for j in range(words_block_count):
        
            
    #提取各个文字块的位置
        location=words_block_list[j]["location"]
        x1=location[0][0]
        x2=location[1][0]
        x3=location[2][0]
        x4=location[3][0]
        y1=location[0][1]
        y2=location[1][1]
        y3=location[2][1]
        y4=location[3][1]
                        
        #计算中心店的位置
        center[j]=[(x1+x2+x3+x4)/4,(y1+y2+y3+y4)/4,]
                        
        #计算每个模块的高度
        height[j]=round(math.sqrt(((x3-x2)**2)+((y3-y2)**2)))
        temp[j]=round(math.sqrt(((x3-x2)**2)+((y3-y2)**2)))
                    
        #计算每个模块的长度
       
        length[j]=round(math.sqrt(((x2-x1)**2)+((y2-y1)**2)))
            
        #计算每个模块的坡度
        slop[j]=(y2-y1)/(x2-x1)
          
           
    #对高度进行排序，筛选，计算标准值scale 
    temp.sort(reverse=True)
  
    if len(temp)>3:
        scale=(temp[1]+temp[2])/2
    else:
        scale=temp[0]
     
        
    #提取有效高度，用于筛选有效文字
    scale=round(scale*0.6)
    
    #识别出的文字高度，如果低于scale，全部清空
    for i in range(words_block_count):
        if (height[i]<scale):
            words_block_list[i]["words"]=""
            flag[i]=0               
        #else:
            #fo.write(words_block_list[i]["words"])
            
    for i in range(words_block_count-1):
        if flag[i]==1:
            #print('片头：'+str(words_block_list[i]["words"]))    
            for j in range(i+1,words_block_count):
                if flag[j]==1:
                #两个字符块之间的纵向距离如果小于scale*1.4，认为两个是在一行，这时需要对比横向坐标
                #前面的宽度做了压缩，现在进行反向调整
                    
                    if abs(center[j][1]-center[i][1])<(scale*1.4):
                        if (center[i][0]-center[j][0])>0:
                        #横向坐标小的排在前面
                           
                            words_block_list[i],words_block_list[j]=words_block_list[j],words_block_list[i]
                            center[i],center[j]=center[j],center[i]
                           
                    elif ((center[j][1]-center[i][1])<0):
                       
                        #更换两个字符块以及相关的坐标信息
                        words_block_list[i],words_block_list[j]=words_block_list[j],words_block_list[i]
                        center[i],center[j]=center[j],center[i]
                #print('片尾：'+str(words_block_list[i]["words"]))      
        #print(words_block_list[i]["words"])
        fo.write(words_block_list[i]["words"])
    
    fo.write(words_block_list[words_block_count-1]["words"])
    fo.write('\n')
    fo.close
    

if __name__ == '__main__':
    
    readnote_request()
