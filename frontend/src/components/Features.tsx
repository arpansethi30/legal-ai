import Image from 'next/image';

const features = [
  {
    title: 'Document Analysis',
    description: 'Automatically extract key information from legal documents using advanced NLP techniques.',
    icon: '/icons/document.svg',
  },
  {
    title: 'Contract Review',
    description: 'Identify potential risks and opportunities in contracts with our AI-powered analysis engine.',
    icon: '/icons/contract.svg',
  },
  {
    title: 'Legal Research',
    description: 'Find relevant case law and statutes in seconds with our intelligent search capabilities.',
    icon: '/icons/research.svg',
  },
  {
    title: 'Clause Library',
    description: 'Access a vast library of pre-vetted legal clauses for quick document assembly.',
    icon: '/icons/library.svg',
  },
  {
    title: 'Risk Assessment',
    description: 'Get a comprehensive risk assessment for your legal documents and business operations.',
    icon: '/icons/risk.svg',
  },
  {
    title: 'Compliance Monitoring',
    description: 'Stay up-to-date with changing regulations and ensure your documents remain compliant.',
    icon: '/icons/compliance.svg',
  },
];

const Features = () => {
  return (
    <section id="features" className="py-16 md:py-24 px-6 md:px-12 bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Powerful Features for Legal Professionals
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Our AI-powered platform offers a suite of tools designed specifically for the legal industry.
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300"
            >
              <div className="flex items-center mb-4">
                <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg mr-4">
                  <div className="w-8 h-8 relative">
                    <Image
                      src={feature.icon}
                      alt={feature.title}
                      fill
                      className="text-blue-600 dark:text-blue-400"
                    />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{feature.title}</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features; 