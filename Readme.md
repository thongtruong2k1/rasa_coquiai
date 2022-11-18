**Sản phẩm sử dụng [rasa](https://rasa.com/) version 3, yêu cầu python version <3.8 (nên sử dụng python=3.7.15)**
> Tạo môi trường ảo để sử dụng:
* `conda create -n name_env python=3.7.15`
* `conda activate name_env`

> Cài đặt các thư viện cần thiết:
* `pip install -r requirements`
> Cài đặt model cần thiết cho việc sử dụng STT và TTS (coqui-ai):
* [model](https://coqui.ai/models): Các model có thể sử dụng.
* [Model Card - v1.0.0-huge-vocab](https://coqui.ai/english/coqui/v1.0.0-huge-vocab): Model sản phẩm đang sử dụng.
* Lưu model vào folder tùy chọn và thay đổi đường dẫn mặc định thành nơi chứa model của bạn tại dòng **124** file ***channel/channel_coquiai.py***

> Sử dụng sản phẩm, có thể tham khảo các [Lệnh](https://rasa.com/docs/rasa/command-line-interface/) của rasa:
* `rasa train`: Dùng để train dữ liệu có sẵn, người dùng có thể thay đổi tập dữ liệu train theo sở thích.
* `rasa interactive`: Vừa train vừa test model vừa train.
* `rasa run --enable-api --credentials ./credentials.yml`: Kích hoạt server, người dùng có thể gửi request về địa chỉ vừa kích hoạt.

**Sản phẩm hiện tại chỉ sử dụng được với file .wav, có thể sử dụng *POSTMAN* để gửi request như hình dưới.**

-----------------------------------------------------------------
![Ant](https://i.ibb.co/xsqZg3k/Screenshot-2022-11-18-124226.png)
