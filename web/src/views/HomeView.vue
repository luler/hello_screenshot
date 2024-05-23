<style>

.paddingContent {
  padding: 0 10px;
}

.inputContainer {
  display: inline-block;
  width: 100%;
  margin-top: 50px;
}

.image-container {
  position: relative;
//width: fit-content; /* 或者设置具体宽度 */
}

.image-container .overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.1); /* 半透明黑色背景 */
}

/* 媒体查询，当屏幕宽度大于768px时，应用以下样式 */
@media (min-width: 768px) {
  .paddingContent {
    padding: 0 80px;
  }

  .inputContainer {
    display: inline-block;
    width: 60%;
    margin-top: 50px;
  }
}
</style>
<template>
  <div class="common-layout">
    <el-container>
      <el-header style="border-bottom: 1px solid #f2f2f2">
        <div class="paddingContent">
          <h3 style="line-height: 60px;float: left;">Hello Screenshot</h3>
          <a style="line-height: 60px;float: right" href="https://github.com/luler/hello_screenshot"
             target="_blank">Github</a>
        </div>
      </el-header>
      <el-main>
        <div class="paddingContent">
          <div style="text-align: center">
            <div class="inputContainer">
              <el-form
                  ref="formRef"
                  :model="formData"
              >
                <el-input
                    size="large"
                    placeholder="请输入网页链接"
                    v-model="formData.url"
                >
                  <template #append>
                    <el-button :loading="btnLoading" @click="submitForm">抓取截图</el-button>
                  </template>
                </el-input>
                <div style="padding-top:40px;display: flex;gap: 20px;flex-wrap: wrap;">
                  <el-form-item label="截图类型：">
                    <el-segmented v-model="formData.full_page_str" :options="['窗口页面','整个网页']"/>
                  </el-form-item>
                  <el-form-item label="窗口大小：">
                    <el-select
                        v-model="formData.viewport_type"
                        style="width: 120px"
                    >
                      <el-option value="1" label="1280*720"/>
                      <el-option value="2" label="1920*1080"/>
                    </el-select>
                  </el-form-item>
                  <el-form-item label="等待加载(秒)：">
                    <el-slider v-model="formData.wait_second" :min="0" :max="10" style="width: 120px"/>
                  </el-form-item>
                </div>

              </el-form>
              <el-divider/>

              <div class="image-container" @mouseenter="()=>{if(isSuccess)showOverlay=true;}"
                   @mouseleave="showOverlay = false">
                <el-image ref="image-1" :src="screenshotUrl" @load="imageLoad(true)" @error="imageLoad(false)"
                          placeholder="正在加载中...">
                  <template #error>
                    <div>截图在此处显示...</div>
                  </template>
                </el-image>
                <div
                    v-show="showOverlay"
                    class="overlay"
                    @mouseenter="(e)=>e.stopPropagation()"
                    @mouseleave="showOverlay = false"
                >
                  <el-button style="margin-top: 50px;" type="primary" @click.prevent="downloadImage('image-1')"
                             size="large"
                             plain>
                    下载
                  </el-button>

                </div>
              </div>

            </div>

          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>


<script>

import {ref} from "vue";

export default {
  setup() {
    const showOverlay = ref(false);
    const isSuccess = ref(false);
    const screenshotUrl = ref('')
    const btnLoading = ref(false)
    const formData = ref({
      url: '',
      full_page_str: '窗口页面',
      viewport_type: '1',
      wait_second: 0,
    })
    const formRef = ref(null)
    const submitForm = () => {
      var data = formData.value
      switch (data.viewport_type) {
        case '1':
          data.viewport_width = 1280
          data.viewport_height = 720
          break;
        case '2':
          data.viewport_width = 1920
          data.viewport_height = 1080
          break;
      }
      if (data.full_page_str === '窗口页面') {
        data.full_page = 0
      } else {
        data.full_page = 1
      }

      data.r = Math.random()
      const queryParams = new URLSearchParams(data);
      btnLoading.value = true
      isSuccess.value = false
      screenshotUrl.value = '/screenshot?' + queryParams
    }
    const imageLoad = (is) => {
      btnLoading.value = false
      isSuccess.value = is
    }
    return {
      formData,
      formRef,
      submitForm,
      screenshotUrl,
      imageLoad,
      btnLoading,
      showOverlay,
      isSuccess,
    }
  },
  data() {
    return {}
  },
  methods: {
    downloadImage(id) {
      const elImageComponent = this.$refs[id]
      const img = elImageComponent.$el.querySelector('img')
      // console.log(img)
      // 创建canvas并绘制图片
      const canvas = document.createElement('canvas')
      canvas.width = img.naturalWidth
      canvas.height = img.naturalHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0)

      canvas.toBlob((blob) => {
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `downloaded_screenshot.png`
        link.click()
        URL.revokeObjectURL(link.href)
      }, 'image/png')
    },
  }
}
</script>