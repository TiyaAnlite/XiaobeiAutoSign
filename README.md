# XiaobeiAutoSign
小北学生签到工具

### 基本使用

#### 安装依赖

1.安装Python3.6及以上版本

2.安装Python库依赖

```
pip install -r requirements.txt
```

或者

```
python -m pip install -r requirements.txt
```

如果你运行在Linux环境，请视情况将`pip`和`python`替换为`pip3`和`python3`

#### 配置用户信息

修改根目录下的`user.conf`，将`username`和`password`修改为自己的用户名和密码

运行`xiaobei.py`，签到完成时返回`>>>Sign success<<<`字样，若提示`Will force sign, continue?`则自行选择输入`Y`或`N`选择继续重复签到，重复签到不会覆盖已有的记录，且无法在客户端展现。显示`>>>Sign failed<<<`则会打印相应错误信息

### 进阶配置

根目录下的`location.conf`是签到时使用的位置信息文件，签到地点的配置是一个区域，不同用户采用的位置信息由`user.conf`中的`location`确定，必须是`location.conf`中存在的配置，否则会导致运行错误

以下表格列出了`loaction.conf`中每个属性的释义

| 键          | 值    | 释义                               |
| ----------- | ----- | ---------------------------------- |
| lon_a       | 经度A | 经度区间的一个点，需要去除小数点   |
| lon_b       | 经度B | 经度区间的另一个点，需要去除小数点 |
| lat_a       | 纬度A | 纬度区间的另一个点，需要去除小数点 |
| lat_b       | 纬度B | 纬度区间的另一个点，需要去除小数点 |
| accuracy    | 精度  | 标识以上的值精确到小数点后几位     |
| coordinates | 地区  | 地区信息                           |

经纬度信息需要去除小数点，且要保证精度均一致，否则可能导致错误

***若要存储经度113.581462，则实际存储的lon_x的值为113581462，accuracy为6，并且要保证其余的lon_x和lat_x精度均为6***

由lon_a,lon_b,lat_a,lat_b四个点构成的矩形空间，就是这个位置的签到区域

### 注意事项

请不要随意修改`.conf`文件的数据结构，包括在不了解CONF文件格式的情况下增加/删除配置信息，以及修改文件编码等

特别是`location.conf`由于包含中文字符已经被规范化为UTF-8，改变文件编码会导致错误