/**
 * 编辑器样式优化验证脚本
 * 
 * 在浏览器控制台中运行此脚本，验证样式优化是否正常工作
 * 
 * 使用方法：
 * 1. 打开编辑器页面
 * 2. 打开浏览器开发者工具（F12）
 * 3. 切换到 Console 标签
 * 4. 复制并粘贴此脚本
 * 5. 按 Enter 执行
 */

(function() {
  console.log('=== 编辑器样式优化验证 ===\n');
  
  // 1. 查找编辑器 iframe
  const iframe = document.querySelector('.custom-editor-container iframe');
  if (!iframe) {
    console.error('❌ 未找到编辑器 iframe');
    return;
  }
  console.log('✅ 找到编辑器 iframe');
  
  // 2. 检查 iframe 文档
  const doc = iframe.contentDocument;
  if (!doc) {
    console.error('❌ 无法访问 iframe 文档');
    return;
  }
  console.log('✅ 可以访问 iframe 文档');
  
  // 3. 检查样式标签
  const head = doc.head;
  if (!head) {
    console.error('❌ 未找到 iframe head');
    return;
  }
  
  const allStyles = head.querySelectorAll('style');
  console.log(`\n📊 样式统计：`);
  console.log(`   总样式数量: ${allStyles.length}`);
  
  // 4. 分类统计样式
  const styleCategories = {
    template: [],
    fieldBlock: [],
    templateRoot: [],
    liveMapping: [],
    other: []
  };
  
  allStyles.forEach((style, index) => {
    const id = style.id || `unnamed-${index}`;
    const length = style.textContent?.length || 0;
    
    if (id.startsWith('template-style')) {
      styleCategories.template.push({ id, length });
    } else if (id === 'field-block-style') {
      styleCategories.fieldBlock.push({ id, length });
    } else if (id === 'template-root-style') {
      styleCategories.templateRoot.push({ id, length });
    } else if (id === 'live-mapping-style') {
      styleCategories.liveMapping.push({ id, length });
    } else {
      styleCategories.other.push({ id, length });
    }
  });
  
  console.log(`\n📋 样式分类：`);
  console.log(`   模板样式 (template-style-*): ${styleCategories.template.length}`);
  console.log(`   字段块样式 (field-block-style): ${styleCategories.fieldBlock.length}`);
  console.log(`   模板根样式 (template-root-style): ${styleCategories.templateRoot.length}`);
  console.log(`   实时映射样式 (live-mapping-style): ${styleCategories.liveMapping.length}`);
  console.log(`   其他样式: ${styleCategories.other.length}`);
  
  // 5. 检查是否有重复的样式
  const styleIds = Array.from(allStyles).map(s => s.id).filter(Boolean);
  const duplicates = styleIds.filter((id, index) => styleIds.indexOf(id) !== index);
  
  if (duplicates.length > 0) {
    console.warn(`\n⚠️  发现重复的样式 ID: ${duplicates.join(', ')}`);
  } else {
    console.log(`\n✅ 没有重复的样式 ID`);
  }
  
  // 6. 检查模板样式内容
  if (styleCategories.template.length > 0) {
    console.log(`\n📝 模板样式详情：`);
    styleCategories.template.forEach(({ id, length }) => {
      console.log(`   ${id}: ${length} 字符`);
    });
  } else {
    console.warn(`\n⚠️  未找到模板样式（可能还未加载模板）`);
  }
  
  // 7. 检查基础样式
  const hasFieldBlock = styleCategories.fieldBlock.length > 0;
  const hasTemplateRoot = styleCategories.templateRoot.length > 0;
  const hasLiveMapping = styleCategories.liveMapping.length > 0;
  
  console.log(`\n🔍 基础样式检查：`);
  console.log(`   字段块样式: ${hasFieldBlock ? '✅' : '❌'}`);
  console.log(`   模板根样式: ${hasTemplateRoot ? '✅' : '❌'}`);
  console.log(`   实时映射样式: ${hasLiveMapping ? '✅' : '❌'}`);
  
  // 8. 检查 template-root 元素
  const body = doc.body;
  const templateRoot = body?.querySelector('#template-root');
  
  if (templateRoot) {
    console.log(`\n✅ 找到 template-root 元素`);
    
    // 检查页面结构
    const pages = templateRoot.querySelectorAll('.template-page');
    console.log(`   页面数量: ${pages.length}`);
    
    // 检查页边距
    const padding = templateRoot.style.getPropertyValue('--template-page-padding');
    console.log(`   页边距: ${padding || '未设置'}`);
  } else {
    console.warn(`\n⚠️  未找到 template-root 元素（可能还未加载内容）`);
  }
  
  // 9. 性能建议
  console.log(`\n💡 性能评估：`);
  
  const totalStyleLength = Array.from(allStyles).reduce((sum, style) => {
    return sum + (style.textContent?.length || 0);
  }, 0);
  
  console.log(`   总样式大小: ${(totalStyleLength / 1024).toFixed(2)} KB`);
  
  if (allStyles.length > 20) {
    console.warn(`   ⚠️  样式数量较多 (${allStyles.length})，可能影响性能`);
  } else {
    console.log(`   ✅ 样式数量合理 (${allStyles.length})`);
  }
  
  if (duplicates.length > 0) {
    console.warn(`   ⚠️  存在重复样式，建议优化`);
  } else {
    console.log(`   ✅ 无重复样式`);
  }
  
  // 10. 总结
  console.log(`\n=== 验证完成 ===`);
  
  const issues = [];
  if (!hasFieldBlock) issues.push('缺少字段块样式');
  if (!hasTemplateRoot) issues.push('缺少模板根样式');
  if (!hasLiveMapping) issues.push('缺少实时映射样式');
  if (duplicates.length > 0) issues.push('存在重复样式');
  
  if (issues.length === 0) {
    console.log('✅ 所有检查通过！样式优化正常工作。');
  } else {
    console.warn(`⚠️  发现 ${issues.length} 个问题：`);
    issues.forEach(issue => console.warn(`   - ${issue}`));
  }
  
  // 11. 返回详细信息供进一步分析
  return {
    iframe,
    doc,
    allStyles: Array.from(allStyles).map(s => ({
      id: s.id,
      length: s.textContent?.length || 0,
      preview: s.textContent?.substring(0, 100)
    })),
    styleCategories,
    duplicates,
    templateRoot,
    summary: {
      totalStyles: allStyles.length,
      totalSize: totalStyleLength,
      hasBasicStyles: hasFieldBlock && hasTemplateRoot && hasLiveMapping,
      hasDuplicates: duplicates.length > 0,
      issues
    }
  };
})();
